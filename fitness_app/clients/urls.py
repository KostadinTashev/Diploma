from django.urls import path
from .views import client_details, client_edit, client_delete, dashboard, client_workouts_view, submit_trainer_review, \
    submit_app_review, client_settings

urlpatterns = [

    path('<int:pk>/<str:username>/', client_details, name='client details'),
    path('<int:client_id>/<str:username>/settings', client_settings, name='client settings'),
    path('edit/', client_edit, name='client edit'),
    path('delete/', client_delete, name='client delete'),
    path('dashboard/<int:client_id>/<str:username>/', dashboard, name='dashboard'),
    path('dashboard/<int:client_id>/<str:username>/workouts/', client_workouts_view, name='client workouts'),
    path('trainer/<int:trainer_id>/review/', submit_trainer_review, name='submit_trainer_review'),
    path('submit-app-review/', submit_app_review, name='submit_app_review'),

]
