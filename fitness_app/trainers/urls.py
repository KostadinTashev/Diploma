from django.urls import path, include
from .views import AllTrainersView, trainer_details, trainer_edit, trainer_delete, MyTrainerView, \
    clients_details, suitable_trainers, choose_trainer, TrainerClientsView, trainer_dashboard

# from ..clients.views import TrainerClientsView

urlpatterns = [
    path('all/', AllTrainersView, name='all trainers'),
    path('my-trainer/', MyTrainerView.as_view(), name='my trainer'),
    path('my-clients/<int:trainer_id>/', TrainerClientsView.as_view(), name='trainer clients'),
    path('clients/<int:client_id>/', clients_details, name='clients_details'),
    path('suitable-trainers/', suitable_trainers, name='suitable trainers'),
    path('trainer/<int:trainer_id>/', choose_trainer, name='choose trainer'),
    path('dashboard/<int:trainer_id>/<str:username>/', trainer_dashboard, name='trainer dashboard'),
    path('<int:pk>/<str:trainer_name>/', include([
        path('', trainer_details, name='trainer details'),
        path('edit/', trainer_edit, name='trainer edit'),
        path('delete/', trainer_delete, name='trainer delete'),
    ]))
]
