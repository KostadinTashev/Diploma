from django.urls import path
from .views import RegisterUserView, LoginUserView, logout_user, profile, admin_dashboard, admin_users_list, \
    admin_trainers_list, admin_clients_list, admin_progress_list, admin_exercises_list, admin_plans_list, \
    admin_user_edit, admin_user_details, admin_user_create, delete_user, toggle_user_active_status, \
    admin_trainer_create, admin_trainer_details, admin_trainer_edit, admin_trainer_delete, admin_client_details, \
    admin_client_edit, admin_client_create, admin_client_delete, admin_progress_details, admin_progress_edit, \
    admin_progress_create, admin_progress_delete, admin_exercise_create, admin_exercise_details, admin_exercise_edit, \
    admin_exercise_delete, admin_meals_list, admin_meal_details, admin_meal_edit, admin_meal_delete, ConfirmEmailView, \
    admin_reviews_list, approve_review, reject_review, admin_workouts_list, admin_workout_create, admin_workout_details, \
    admin_workout_edit, admin_workout_delete, admin_program_list, admin_program_create, admin_program_details, \
    admin_program_edit, admin_program_delete, admin_products_list, admin_product_create, admin_product_details, \
    admin_product_edit, admin_product_delete, admin_plan_create, admin_plan_details, admin_plan_edit, admin_plan_delete
from ..clients.views import set_client_data
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register user'),
    path('accounts/confirm-email/<uidb64>/<token>/', ConfirmEmailView.as_view(), name='confirm_email'),
    path('activate/<uidb64>/<token>/', ConfirmEmailView.as_view(), name='confirm_email'),
path('password-reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
    path('set-client-data/<int:client_id>/', set_client_data, name='set client data'),
    path('login/', LoginUserView.as_view(), name='login user'),
    path('logout/', logout_user, name='logout user'),
    path('profile/', profile, name='profile'),
    path('admin-dashboard/', admin_dashboard, name='admin dashboard'),
    path('admin/users/', admin_users_list, name='admin users list'),
    path('admin/users/add/', admin_user_create, name='admin user create'),
    path('admin/users/<int:user_id>/', admin_user_details, name='admin user details'),
    path('admin/users/<int:user_id>/edit/', admin_user_edit, name='admin user edit'),
    path('admin/users/<int:pk>/toggle/', toggle_user_active_status, name='admin user toggle'),
    path('admin/users/<int:user_id>/delete/', delete_user, name='admin user delete'),
    path('admin/trainers/', admin_trainers_list, name='admin trainers list'),
    path('admin/trainers/create/', admin_trainer_create, name='admin trainer create'),
    path('admin/trainers/<int:trainer_id>/', admin_trainer_details, name='admin trainer details'),
    path('admin/trainers/<int:trainer_id>/edit/', admin_trainer_edit, name='admin trainer edit'),
    path('admin/trainers/<int:trainer_id>/delete/', admin_trainer_delete, name='admin trainer delete'),
    path('admin/clients/', admin_clients_list, name='admin clients list'),
    path('admin/clients/<int:client_id>/', admin_client_details, name='admin client details'),
    path('admin/clients/<int:client_id>/edit/', admin_client_edit, name='admin client edit'),
    path('admin/clients/create/', admin_client_create, name='admin client create'),
    path('admin/clients/<int:client_id>/delete/', admin_client_delete, name='admin client delete'),
    path('admin/progress/', admin_progress_list, name='admin progress list'),
    path('admin/progress/<int:progress_id>/', admin_progress_details, name='admin progress details'),
    path('admin/progress/<int:progress_id>/edit/', admin_progress_edit, name='admin progress edit'),
    path('admin/progress/create/', admin_progress_create, name='admin progress create'),
    path('admin/progress/<int:progress_id>/delete/', admin_progress_delete,
         name='admin progress delete'),
    path('admin/exercises/', admin_exercises_list, name='admin exercises list'),
    path('admin/exercises/create/', admin_exercise_create, name='admin exercise create'),
    path('admin/exercises/<int:exercise_id>/', admin_exercise_details, name='admin exercise details'),
    path('admin/exercises/<int:exercise_id>/edit/', admin_exercise_edit, name='admin exercise edit'),
    path('admin/exercises/<int:exercise_id>/delete/', admin_exercise_delete, name='admin exercise delete'),
    path('admin/meals/', admin_meals_list, name='admin meals list'),
    path('admin/meals/create/', admin_exercise_create, name='admin meal create'),
    path('admin/meals/<int:meal_id>/', admin_meal_details, name='admin meal details'),
    path('admin/meals/<int:meal_id>/edit/', admin_meal_edit, name='admin meal edit'),
    path('admin/meals/<int:meal_id>/delete/', admin_meal_delete, name='admin meal delete'),
    path('admin/reviews/', admin_reviews_list, name='admin reviews list'),
    path('admin/reviews/<int:review_id>/approve/', approve_review, name='approve review'),
    path('admin/reviews/<int:review_id>/reject/', reject_review, name='reject review'),
path('admin/workouts/',                       admin_workouts_list,    name='admin workouts list'),
path('admin/workouts/create/',                admin_workout_create,   name='admin workout create'),
path('admin/workouts/<int:workout_id>/',      admin_workout_details,  name='admin workout details'),
path('admin/workouts/<int:workout_id>/edit/', admin_workout_edit,     name='admin workout edit'),
path('admin/workouts/<int:workout_id>/delete/',admin_workout_delete,  name='admin workout delete'),
    path("admin/programs/", admin_program_list, name="admin program list"),
    path("admin/programs/create/", admin_program_create, name="admin program create"),
    path("admin/programs/<int:pk>/", admin_program_details, name="admin program details"),
    path("admin/programs/<int:pk>/edit/", admin_program_edit, name="admin program edit"),
    path("admin/programs/<int:pk>/delete/", admin_program_delete, name="admin program delete"),
    path("admin/products/", admin_products_list, name="admin products list"),
    path("admin/products/add/", admin_product_create, name="admin product create"),
    path("admin/products/<int:pk>/", admin_product_details, name="admin product detail"),
    path("admin/products/<int:pk>/edit/", admin_product_edit, name="admin product edit"),
    path("admin/products/<int:pk>/delete/", admin_product_delete, name="admin product delete"),

    path("admin/plans/", admin_plans_list, name="admin plans list"),
    path("admin/plans/add/", admin_plan_create, name="admin plan add"),
    path("admin/plans/<int:pk>/", admin_plan_details, name="admin plan detail"),
    path("admin/plans/<int:pk>/edit/", admin_plan_edit, name="admin plan edit"),
    path("admin/plans/<int:pk>/delete/", admin_plan_delete, name="admin plan delete"),
]
