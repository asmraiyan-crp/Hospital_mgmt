from rest_framework import serializers
from .models import TransportFlow, Resource

class TransportFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportFlow
        fields = ['id', 'A', 'to', 'max_capacity']

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'name', 'volume', 'priority_score', 'quantity']

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

class MaxFlowInputSerializer(serializers.Serializer):
    source = serializers.CharField(max_length=100)
    sink = serializers.CharField(max_length=100)
    
    def validate(self, data):
        if data['source'].lower() == data['sink'].lower():
            raise serializers.ValidationError("Source and Sink cannot be the same.")
        return data