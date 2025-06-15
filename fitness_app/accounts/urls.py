from django.urls import path
from .views import RegisterUserView, LoginUserView, logout_user, profile, admin_dashboard
from ..clients.views import set_client_data

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register user'),
    path('set-client-data/<int:client_id>/', set_client_data, name='set client data'),
    path('login/', LoginUserView.as_view(), name='login user'),
    path('logout/', logout_user, name='logout user'),
    path('profile/', profile, name='profile'),
    path('admin-dashboard/', admin_dashboard, name='admin dashboard'),

]
