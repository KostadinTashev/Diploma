from django.urls import path

from fitness_app.program_exercises.views import assign_program_view, edit_program,client_program_view

urlpatterns = [
    path('assign/<int:client_id>/', assign_program_view, name='assign program'),
    path('edit_program/<int:client_id>/', edit_program, name='edit program'),
    path('client_program/<int:client_id>/', client_program_view, name='client_program'),
]
