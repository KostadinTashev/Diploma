from django.urls import path, include

from .views import exercises, exercise_add, exercise_details, exercise_edit, exercise_delete, complete_exercise, \
    uncomplete_exercise

urlpatterns = [
    path('', exercises, name='exercises'),
    path('add/', exercise_add, name='exercise add'),
    # path('api/exercises/', exercises_api, name='exercises_api'),
    path('exercise/<int:pk>/complete/', complete_exercise, name='exercise complete'),
    path('exercise/<int:pk>/uncomplete/', uncomplete_exercise, name='exercise uncomplete'),
    path('<int:pk>/<str:exercise_name>/', include([
        path('', exercise_details, name='exercise details'),
        path('edit/', exercise_edit, name='exercise edit'),
        path('delete/', exercise_delete, name='exercise delete'),

    ]))

]
