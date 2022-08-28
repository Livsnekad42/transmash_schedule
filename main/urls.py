"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from django.views.generic import TemplateView

from rest_framework.schemas import get_schema_view
from rest_framework.permissions import AllowAny

from swagger.schema_view import MyOpenAPIRenderer, CustomSchema

urlpatterns = [
    path('admin_a195abe937af4f5ab2b/', admin.site.urls),
    path('admin/', include(('administration.urls', 'administration'), namespace='administration'), name="administration"),
    path('auth/', include(('authentication.urls', 'authentication'), namespace='authentication')),
    path('employee/', include(('employee.urls', 'employee'), namespace='employee')),
    path('profile/', include(('profiles.urls', 'profiles'), namespace='profile'), name="profile"),
    path('geo/', include(('geo_city.urls', 'geo'), namespace='geo'), name="geo"),
    path('company/', include(('company.urls', 'company'), namespace='company'), name="company"),
    path('public/', include(('company.public_urls', 'company__public'),
                            namespace='company__public'), name="company__public"),

    path('openapi/', get_schema_view(
        title="API docs",
        description="API developers",
        permission_classes=[AllowAny],
        public=True,
        renderer_classes=[MyOpenAPIRenderer],
        generator_class=CustomSchema,
    ), name='openapi-schema'),
    path('docs/', TemplateView.as_view(
        template_name='documentation.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),
]

if settings.DEBUG:
    if settings.MEDIA_ROOT:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Эта строка опциональна и будет добавлять url'ы только при DEBUG = True
urlpatterns += staticfiles_urlpatterns()