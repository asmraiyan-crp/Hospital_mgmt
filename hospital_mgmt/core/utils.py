from .maxflow import maxflow
from .knapsack import solve_knapsack
from .models import (
    Resource, TransportFlow, supply_max_cap
)
from django.db import transaction
from django.db.models import F
from collections import defaultdict

def calculate_single_pair_flow(source_name, sink_name):
    """
    STAGE 1:
    Calculates max-flow and saves the flow from the source to its 
    immediate neighbors into the 'supply_max_cap' table.
    """
    mf = maxflow()
    all_routes = TransportFlow.objects.all()

    print("Building undirected graph...")
    for route in all_routes:
        mf.add_edge(route.A, route.to, route.max_capacity)
        mf.add_edge(route.to, route.A, route.max_capacity)
    
    print(f"Graph built. Calculating max-flow from {source_name} to {sink_name}...")
    total_flow = mf.mflow(source_name, sink_name)
    print(f"Calculation complete. Total flow: {total_flow}")
    print(f"Saving immediate flows from source '{source_name}'...")
    try:
        assignments = mf.get_flow() 
        
        if source_name in assignments:
            immediate_flows = assignments[source_name]

            with transaction.atomic():
                supply_max_cap.objects.all().delete()
                
                new_caps = []
                for neighbor_node, flow_amount in immediate_flows.items():
                    if flow_amount > 0:
                        new_caps.append(
                            supply_max_cap(
                                name=neighbor_node,
                                capacity=flow_amount
                            )
                        )
                        print(f"  Saving: {source_name} → {neighbor_node} = {flow_amount} units")
                
                supply_max_cap.objects.bulk_create(new_caps)
        else:
            print(f"Warning: Source node '{source_name}' not found in flow results.")
            
    except Exception as e:
        print(f"ERROR saving flow assignments: {e}")

    return total_flow

def run_supply_optimization():
    """
    STAGE 2:
    Runs knapsack optimization for *each* flow capacity saved in
    the 'supply_max_cap' table.
    """
    print("Running Knapsack optimization for each supply node...")
    
    node_capacities = list(supply_max_cap.objects.all())
    
    if not node_capacities:
        print("No capacities found in 'supply_max_cap' table. Run flow calculation first.")
        return {}, 0.0

    available_resources = list(Resource.objects.filter(
        route_name__isnull=True, 
        volume__gt=0
    ))
    
    all_allocated_item_ids = set()
    
    items_to_update = []
    
    selections_summary = {}
    total_value_all_nodes = 0.0

    for entry in node_capacities:
        node_name = entry.name
        knapsack_capacity = entry.capacity
        
        print(f"Running Knapsack for '{node_name}' with capacity: {knapsack_capacity}")

        current_available_items = [
            item for item in available_resources 
            if item.id not in all_allocated_item_ids
        ]
        
        if not current_available_items:
            print(f"  No available resources left for '{node_name}'.")
            continue

        selected_items, total_value = solve_knapsack(knapsack_capacity, current_available_items)
        
        selections_summary[node_name] = selected_items
        total_value_all_nodes += total_value
        
        for item in selected_items:
            all_allocated_item_ids.add(item.id)
            
            item.route_name = node_name 
            item.volume = 0
            items_to_update.append(item)
            
        selected_names = ", ".join([item.name for item in selected_items])
        print(f"  '{node_name}' will send: {selected_names} (Value: {total_value})")

    with transaction.atomic():
        Resource.objects.bulk_update(items_to_update, ['route_name', 'volume'])

    print("Optimization complete! Resources have been assigned and volume set to 0.")
    return selections_summary, total_value_all_nodes