from django.urls import path
from .views import client_details, client_edit, client_delete, dashboard

urlpatterns = [

    path('<int:pk>/<str:username>/', client_details, name='client details'),
    # path('set-client-data/<int:client_id>/', set_client_data, name='set client data'),

    path('edit/', client_edit, name='client edit'),
    path('delete/', client_delete, name='client delete'),
    path('dashboard/<int:client_id>/<str:username>/',dashboard, name='dashboard')
]
