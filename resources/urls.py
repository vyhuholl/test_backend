"""URL patterns for resource endpoints."""

from django.urls import path

from resources.views import (
    DocumentCreateView,
    DocumentDetailView,
    DocumentListView,
    ProjectListView,
)


app_name = "resources"

urlpatterns = [
    # Documents
    path("documents", DocumentListView.as_view(), name="document_list"),
    path("documents/create", DocumentCreateView.as_view(), name="document_create"),
    path("documents/<str:document_id>", DocumentDetailView.as_view(), name="document_detail"),
    
    # Projects
    path("projects", ProjectListView.as_view(), name="project_list"),
]
