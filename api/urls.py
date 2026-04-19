from django.urls import path
from . import views

urlpatterns = [
    path('', views.APIIndexView.as_view(), name='api-index'),
    path('hello/', views.HelloView.as_view(), name='hello'),    
    path('webhook/github/', views.GitHubWebhookView.as_view(), name='github-webhook'),
    path('assets/', views.AssetProxyView.as_view(), name='asset-proxy'),
    path('config/', views.VaultConfigurationView.as_view(), name='vault-config'),
    path('auth/signup/', views.SignUpView.as_view(), name='signup'),
]
