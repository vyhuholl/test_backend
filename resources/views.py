"""Views for mock resource endpoints demonstrating RBAC."""

from datetime import datetime

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import RBACPermission
from core.utils import response_success
from resources.serializers import (
    CreateDocumentSerializer,
    DocumentSerializer,
    ProjectSerializer,
)


# Mock data for demonstration
MOCK_DOCUMENTS = [
    {
        "id": "doc-1",
        "title": "Project Requirements",
        "content": "Detailed requirements for the authentication system...",
        "author": "Admin User",
        "created_at": datetime(2026, 1, 1, 10, 0, 0),
        "updated_at": datetime(2026, 1, 1, 10, 0, 0),
    },
    {
        "id": "doc-2",
        "title": "Technical Specification",
        "content": "Technical details of the RBAC implementation...",
        "author": "Tech Lead",
        "created_at": datetime(2026, 1, 5, 14, 30, 0),
        "updated_at": datetime(2026, 1, 5, 14, 30, 0),
    },
    {
        "id": "doc-3",
        "title": "API Documentation",
        "content": "Complete API documentation for all endpoints...",
        "author": "Developer",
        "created_at": datetime(2026, 1, 7, 9, 15, 0),
        "updated_at": datetime(2026, 1, 7, 9, 15, 0),
    },
]

MOCK_PROJECTS = [
    {
        "id": "proj-1",
        "name": "Authentication System",
        "description": "Custom authentication and authorization system",
        "status": "active",
        "created_at": datetime(2026, 1, 1, 8, 0, 0),
    },
    {
        "id": "proj-2",
        "name": "API Gateway",
        "description": "Central API gateway for microservices",
        "status": "on_hold",
        "created_at": datetime(2025, 12, 15, 10, 0, 0),
    },
]


class DocumentListView(APIView):
    """
    List all documents.
    
    GET /api/resources/documents - Requires documents:read_all_permission
    """
    
    permission_classes = [RBACPermission]
    rbac_element = 'documents'
    
    def get(self, request: Request) -> Response:
        """List all documents."""
        serializer = DocumentSerializer(MOCK_DOCUMENTS, many=True)
        return Response(
            response_success(serializer.data, meta={"total_count": len(MOCK_DOCUMENTS)}),
            status=status.HTTP_200_OK,
        )


class DocumentDetailView(APIView):
    """
    Get a specific document.
    
    GET /api/resources/documents/{id} - Requires documents:read_permission
    """
    
    permission_classes = [RBACPermission]
    rbac_element = 'documents'
    
    def get(self, request: Request, document_id: str) -> Response:
        """Get document by ID."""
        # Find document in mock data
        document = next((doc for doc in MOCK_DOCUMENTS if doc["id"] == document_id), None)
        
        if not document:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "Document not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        serializer = DocumentSerializer(document)
        return Response(
            response_success(serializer.data),
            status=status.HTTP_200_OK,
        )


class DocumentCreateView(APIView):
    """
    Create a new document.
    
    POST /api/resources/documents - Requires documents:create_permission
    """
    
    permission_classes = [RBACPermission]
    rbac_element = 'documents'
    
    def post(self, request: Request) -> Response:
        """Create a new document."""
        serializer = CreateDocumentSerializer(data=request.data)
        
        if not serializer.is_valid():
            serializer.is_valid(raise_exception=True)
        
        # Create mock document
        new_document = {
            "id": f"doc-{len(MOCK_DOCUMENTS) + 1}",
            "title": serializer.validated_data["title"],
            "content": serializer.validated_data["content"],
            "author": request.user.email,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        
        document_serializer = DocumentSerializer(new_document)
        return Response(
            response_success(document_serializer.data),
            status=status.HTTP_201_CREATED,
        )


class ProjectListView(APIView):
    """
    List all projects.
    
    GET /api/resources/projects - Requires projects:read_all_permission
    """
    
    permission_classes = [RBACPermission]
    rbac_element = 'projects'
    
    def get(self, request: Request) -> Response:
        """List all projects."""
        serializer = ProjectSerializer(MOCK_PROJECTS, many=True)
        return Response(
            response_success(serializer.data, meta={"total_count": len(MOCK_PROJECTS)}),
            status=status.HTTP_200_OK,
        )
