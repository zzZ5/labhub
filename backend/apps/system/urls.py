from django.urls import path

from .views import csrf_token, dashboard_summary, health_check

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("csrf/", csrf_token, name="csrf-token"),
    path("dashboard/", dashboard_summary, name="dashboard-summary"),
]
