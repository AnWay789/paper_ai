from django.urls import path

from . import views_ui

app_name = "articles"

urlpatterns = [
    path("", views_ui.dashboard, name="dashboard"),
    path("partials/projects-table/", views_ui.projects_table_partial, name="projects_table_partial"),
    path("projects/new/", views_ui.project_create, name="project_create"),
    path("projects/<uuid:project_id>/edit/", views_ui.project_edit, name="project_edit"),
    path("projects/import/", views_ui.project_import, name="project_import"),
    path("projects/bulk/estimate/", views_ui.bulk_estimate, name="bulk_estimate"),
    path("projects/bulk/start/", views_ui.bulk_start, name="bulk_start"),
    path("projects/<uuid:project_id>/", views_ui.project_detail, name="project_detail"),
    path("projects/<uuid:project_id>/estimate/", views_ui.project_estimate, name="project_estimate"),
    path("projects/<uuid:project_id>/start/", views_ui.project_start, name="project_start"),
    path("projects/<uuid:project_id>/delete/", views_ui.project_delete, name="project_delete"),
]
