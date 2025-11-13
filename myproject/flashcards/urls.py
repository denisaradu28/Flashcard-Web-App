from django.urls import path
from .import views

urlpatterns = [
    path('create/',views.create_set, name='create_set'),
    path('read/',views.read_sets, name='read_sets'),
    path('edit/', views.edit_set, name='edit_set'),
    path('delete/',views.delete_set, name='delete_set'),
]