from django.urls import path, include
from .views import workout_list, workout_add, workout_details, workout_edit, workout_delete

urlpatterns = [
    path('', workout_list, name='workout list'),
    path('add/', workout_add, name='workout add'),
    path('<int:pk>/', include([
        path('', workout_details, name='workout details'),
        path('edit/', workout_edit, name='workout edit'),
        path('delete/', workout_delete, name='workout delete'),
    ])),

]
