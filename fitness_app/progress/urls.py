from django.urls import path
from .views import client_progress_view, client_progress, progress_chart, add_progress

urlpatterns = [
    path('<int:client_id>/', client_progress_view, name='current progress'),
    path('add-progress/', add_progress, name='add_progress'),

    path('progress-chart/', progress_chart, name='progress chart'),
    path('client/<int:pk>/', client_progress, name='client progress'),
]
