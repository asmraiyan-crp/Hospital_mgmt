import csv
import io
import sys
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

# Ensure these imports match your models.py
from .models import TransportFlow, supply_max_cap,Resource
from .serializers import FileUploadSerializer, MaxFlowInputSerializer, TransportFlowSerializer , ResourceSerializer
from .maxflow import maxflow
from .knapsack import solve_knapsack

class SystemStatusView(APIView):
    """
    GET /api/status/
    Checks if the database has network data.
    """
    def get(self, request):
        has_data = TransportFlow.objects.exists()
        return Response({'data_exists': has_data}, status=status.HTTP_200_OK)

class BatchUploadView(APIView):
    """
    POST /api/upload/
    Uploads a CSV file, parses it, and populates the database.
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        print(f"DEBUG: Received Upload Request. Files: {request.FILES.keys()}")

        serializer = FileUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            csv_file = serializer.validated_data['file']
            
            try:
                # Attempt to read and decode
                file_data = csv_file.read()
                decoded_file = file_data.decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.reader(io_string)
                
                # Skip header row
                next(reader, None)
                
                new_entries = []
                for row_idx, row in enumerate(reader):
                    if len(row) >= 3:
                        try:
                            new_entries.append(TransportFlow(
                                A=row[0].strip(),
                                to=row[1].strip(),
                                max_capacity=int(row[2].strip())
                            ))
                        except ValueError as ve:
                            print(f"DEBUG: Row {row_idx} Error: {ve}")
                
                if new_entries:
                    TransportFlow.objects.all().delete()
                    TransportFlow.objects.bulk_create(new_entries)
                    print(f"DEBUG: Successfully created {len(new_entries)} rows.")
                    return Response(
                        {'success': True, 'message': f'Successfully loaded {len(new_entries)} routes.'}, 
                        status=status.HTTP_201_CREATED
                    )
                else:
                     return Response(
                        {'success': False, 'message': 'CSV file was empty or had no valid rows (Source,Dest,Cap).'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

            except UnicodeDecodeError:
                print(">>> UPLOAD ERROR: File is not UTF-8. Is it an Excel (.xlsx) file?")
                return Response(
                    {'success': False, 'message': 'File encoding error. Please ensure it is a valid .CSV (text) file, not Excel.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                print(f">>> UPLOAD ERROR: {str(e)}")
                return Response(
                    {'success': False, 'message': f'Error parsing file: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        print(f">>> UPLOAD ERROR (Serializer): {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MaxFlowCalculationView(APIView):
    """
    POST /api/calculate/
    Input: { "source": "Dhaka", "sink": "Chittagong" }
    Output: Max Flow value, path details, AND saves supply_max_cap data.
    """
    def post(self, request):
        serializer = MaxFlowInputSerializer(data=request.data)
        
        if serializer.is_valid():
            source = serializer.validated_data['source']
            sink = serializer.validated_data['sink']
            
            mf = maxflow()
            routes = TransportFlow.objects.all()
            
            if not routes.exists():
                return Response({'error': 'No network data found in database.'}, status=status.HTTP_404_NOT_FOUND)

            valid_nodes = set()
            for route in routes:
                mf.add_edge(route.A, route.to, route.max_capacity)
                mf.add_edge(route.to, route.A, route.max_capacity)
                valid_nodes.add(route.A)
                valid_nodes.add(route.to)
            
            if source not in valid_nodes:
                return Response(
                    {'error': f"Source '{source}' not found. Available: {list(valid_nodes)[:5]}..."}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            if sink not in valid_nodes:
                 return Response(
                    {'error': f"Destination '{sink}' not found."}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # 1. Calculate Max Flow
            max_val = mf.mflow(source, sink)
            flow_details = dict(mf.get_flow())
            
            # 2. Extract Immediate Neighbors for Knapsack (supply_max_cap)
            new_entries = []
            for u in flow_details:
                for v, f in flow_details[u].items():
                    if u == source and f > 0:
                        # FIX: We must save the 'name' and 'capacity'
                        new_entries.append(supply_max_cap(to=v, capacity=f))
            
            # 3. Save to Database (Silently)
            if new_entries:
                supply_max_cap.objects.all().delete()
                supply_max_cap.objects.bulk_create(new_entries)
                print(f"DEBUG: Saved {len(new_entries)} supply nodes for next stage.")
            
            # 4. Return the FLOW RESULT to the Frontend
            # CRITICAL: Do NOT return the "Saved supply nodes" message here, 
            # or the frontend won't know how to display the graph.
            return Response({
                'max_flow': max_val,
                'details': flow_details,
                'source': source,
                'sink': sink
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResourceUploadView(APIView):
    """
    POST /api/upload/resources/
    Parses a CSV file to bulk create Resource objects.
    Format: Name, Volume, Priority, Quantity
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            csv_file = serializer.validated_data['file']
            
            try:
                file_data = csv_file.read()
                decoded_file = file_data.decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.reader(io_string)
                
                # Skip header
                next(reader, None)
                
                new_resources = []
                for row in reader:
                    # Check if row has at least 4 columns
                    if len(row) >= 4:
                        try:
                            new_resources.append(Resource(
                                name=row[0].strip(),
                                volume=int(row[1].strip()),
                                priority_score=int(row[2].strip()),
                                quantity=int(row[3].strip())
                            ))
                        except ValueError:
                            continue # Skip malformed rows
                
                if new_resources:
                    # Optional: Clear old resources? 
                    # Resource.objects.all().delete() 
                    Resource.objects.bulk_create(new_resources)
                    return Response(
                        {'success': True, 'message': f'Added {len(new_resources)} items to inventory.'}, 
                        status=status.HTTP_201_CREATED
                    )
                else:
                     return Response(
                        {'success': False, 'message': 'CSV was empty or invalid.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

            except Exception as e:
                return Response(
                    {'success': False, 'message': f'Error: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class KnapsackCalculationView(APIView):
    def get(self, request):
        # 1. Get capacities calculated in Stage 1
        supply_nodes = supply_max_cap.objects.all()
        if not supply_nodes.exists():
            return Response({'error': 'No capacity data found. Run MaxFlow (Stage 1) first.'}, status=400)

        # 2. Get all available resources
        all_resources = list(Resource.objects.all())
        if not all_resources:
             return Response({'error': 'No resources found in database. Add items first.'}, status=400)

        results = {}
        available_pool = []
        for r in all_resources:
            count = r.quantity if r.quantity else 1
            for _ in range(count):
                available_pool.append(r)

        for node in supply_nodes:
            # UPDATED: Use 'node.to' as the identifier for the route destination
            destination_name = node.to 
            
            selected, val = solve_knapsack(available_pool, node.capacity)
            
            results[destination_name] = {
                'source': node.A,
                'destination': node.to,
                'capacity': node.capacity,
                'total_priority': val,
                'items': [
                    {'name': item.name, 'volume': item.volume, 'score': item.priority_score}
                    for item in selected
                ]
            }

            for item in selected:
                if item in available_pool:
                    available_pool.remove(item)

        return Response(results, status=200)

class TransportFlowViewSet(viewsets.ModelViewSet):
    queryset = TransportFlow.objects.all().order_by('id')
    serializer_class = TransportFlowSerializer

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all().order_by('id')
    serializer_class = ResourceSerializer
    