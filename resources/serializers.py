"""Serializers for mock resource endpoints."""

from rest_framework import serializers


class DocumentSerializer(serializers.Serializer):
    """Serializer for mock document resource."""
    
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(max_length=200)
    content = serializers.CharField()
    author = serializers.CharField(max_length=100)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class CreateDocumentSerializer(serializers.Serializer):
    """Serializer for creating mock documents."""
    
    title = serializers.CharField(max_length=200, required=True)
    content = serializers.CharField(required=True)


class ProjectSerializer(serializers.Serializer):
    """Serializer for mock project resource."""
    
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=200)
    description = serializers.CharField()
    status = serializers.ChoiceField(choices=['active', 'completed', 'on_hold'])
    created_at = serializers.DateTimeField(read_only=True)
