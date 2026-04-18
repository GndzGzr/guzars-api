from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from api.views import APIIndexView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("", APIIndexView.as_view(), name='root-index'),
    path("admin/", admin.site.urls),
    
    # Swagger & OpenAPI 3 Endpoints
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    
    path("api/", include("api.urls")),
    path("api/auth/token/", obtain_auth_token, name="obtain-token"),
    path("api/", include("notes.urls")),
]
