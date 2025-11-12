from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Resource
from .serializers import product_serializer
# Create your views here.

@api_view()
def product_list(request):
    return Response('ok')

@api_view()
def product_details(request,id):
    product =Resource.objects.get(pk = id)
    serializer = product_serializer(product)

    return Response(serializer.data)
