from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
from rest_framework import permissions

urlpatterns = [
    # Admin URL
    path("admin/", admin.site.urls),
    # Documentation URLs
    path(
        "openapi/",
        get_schema_view(
            title="WineApp",
            description="WineApp API Service",
            public=True,
            permission_classes=(permissions.AllowAny,),
        ),
        name="openapi-schema",
    ),
    path(
        "swagger-ui/",
        TemplateView.as_view(
            template_name="core/documentation.html",
            extra_context={"schema_url": "openapi-schema"},
        ),
        name="swagger-ui",
    ),
    # Module URLs
    # Wine URLs
    path("api/wine/", include("wine.urls")),
    # User URLs
    path("api/user/", include("user.urls")),
]
