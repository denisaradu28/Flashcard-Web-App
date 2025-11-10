from django.urls import path
from .import views

urlpatterns = [
    path('create/',views.create_set, name='create_set'),
    path('read/',views.read_sets, name='read_sets'),
]