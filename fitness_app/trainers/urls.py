from django.urls import path, include
from .views import AllTrainersView, trainer_details, trainer_edit, trainer_delete, MyTrainerView, \
    clients_details, suitable_trainers, choose_trainer, trainer_clients_view, trainer_dashboard, \
    trainer_nutrition_clients, trainer_pending_requests, approve_trainer_request, reject_trainer_request, \
    send_trainer_request
from ..clients.views import request_trainer

# from ..clients.views import TrainerClientsView

urlpatterns = [
    path('all/', AllTrainersView.as_view(), name='all trainers'),
    path('my-trainer/', MyTrainerView.as_view(), name='my trainer'),
    path('my-clients/<int:trainer_id>/', trainer_clients_view, name='trainer clients'),
    path('clients/<int:client_id>/', clients_details, name='clients_details'),
    path('suitable-trainers/', suitable_trainers, name='suitable trainers'),
    path('trainer/<int:trainer_id>/', choose_trainer, name='choose trainer'),
    path('trainer-request/send/<int:trainer_id>/', send_trainer_request, name='send trainer request'),
    path('trainer/pending-requests/', trainer_pending_requests, name='trainer pending requests'),

    path('trainer-request/approve/<int:request_id>/', approve_trainer_request, name='approve trainer request'),
    path('trainer-request/reject/<int:request_id>/', reject_trainer_request, name='reject trainer request'),

    path('dashboard/<int:trainer_id>/<str:username>/', trainer_dashboard, name='trainer dashboard'),
    path('nutrition-plans/clients/', trainer_nutrition_clients, name='trainer nutrition clients'),
    path('<int:pk>/<str:trainer_name>/', include([
        path('', trainer_details, name='trainer details'),
        path('edit/', trainer_edit, name='trainer edit'),
        path('delete/', trainer_delete, name='trainer delete'),
    ]))
]
