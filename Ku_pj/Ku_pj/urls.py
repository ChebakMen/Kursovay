from django.urls import path
from django.contrib import admin
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('set-counts/', views.set_counts, name='set_counts'),
    path('add-criterion/', views.add_criterion, name='add_criterion'),
    path('add-experts/', views.add_experts, name='add_experts'),
    path('add-alternative/', views.add_alternatives, name='add_alternative'),
    path('input-scores/', views.input_scores, name='input_scores'),
    path('calculate-distances/', views.calculate_distances, name='calculate_distances'),
]
