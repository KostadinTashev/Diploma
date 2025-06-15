from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('fitness_app.common.urls')),
    path('accounts/', include('fitness_app.accounts.urls')),
    path('clients/', include('fitness_app.clients.urls')),
    path('exercises/', include('fitness_app.exercises.urls')),
    path('meals/', include('fitness_app.meals.urls')),
    path('program_exercises/', include('fitness_app.program_exercises.urls')),
    path('nutrition_plans/', include('fitness_app.nutrition_plans.urls')),
    path('progress/', include('fitness_app.progress.urls')),
    path('trainers/', include('fitness_app.trainers.urls')),
    path('workouts/', include('fitness_app.workouts.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
