from django.urls import path, include
from .views import plans, plan_add, plan_details, plan_edit, plan_delete

urlpatterns = [
    path('', plans, name='plans'),
    path('add/', plan_add, name='plan add'),
    path('<int:pk>/', include([
        path('', plan_details, name='plan details'),
        path('edit/', plan_edit, name='plan edit'),
        path('delete/', plan_delete, name='plan delete'),
    ]))
]
