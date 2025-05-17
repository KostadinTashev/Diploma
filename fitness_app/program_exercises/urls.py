from django.urls import path

from fitness_app.program_exercises.views import  assign_program_view

urlpatterns = [
    path('assign/<int:client_id>/', assign_program_view, name='assign program'),
]