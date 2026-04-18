from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from api.views import APIIndexView

urlpatterns = [
    path("", APIIndexView.as_view(), name='root-index'),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("api/auth/token/", obtain_auth_token, name="obtain-token"),
    path("api/", include("notes.urls")),
]
