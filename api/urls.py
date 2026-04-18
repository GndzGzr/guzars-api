from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.HelloView.as_view(), name='hello'),
    path('webhook/github/', views.GitHubWebhookView.as_view(), name='github-webhook'),
]
