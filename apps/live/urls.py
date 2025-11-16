from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.StartLiveView.as_view()),
    path('ingest/verify/', views.IngestVerifyView.as_view()),
    path('ingest/done/', views.IngestDoneView.as_view()),
]