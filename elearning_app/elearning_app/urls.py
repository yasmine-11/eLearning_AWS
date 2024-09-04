"""
URL configuration for elearning_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import *
from courses.views import *
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Define schema_view for Swagger API Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="eLearning API",
        default_version='v1',
        description="API documentation for the eLearning application",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@elearning.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('courses/', include('courses.urls')),
    path('', user_login, name='login'),  # Root page for login
    path('communications/', include('communications.urls')),
    path('api/', include('api.urls')), # Include API URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'), # Swagger URL
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)