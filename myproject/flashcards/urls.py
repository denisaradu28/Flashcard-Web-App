from django.urls import path
from .import views

urlpatterns = [
    path('', views.home, name='home'),

    path('create/',views.create_set, name='create_set'),
    path('read/',views.read_sets, name='read_sets'),

    path('set/<str:set_name>/', views.create_set, name='create_set'),
    path('seturi/set//edit/', views.edit_set, name='edit_set'),

    path('view/', views.view_set, name='view_set'),

    path('delete/', views.delete_set, name='delete_set'),

    path('predefinde/', views.predefined_list, name='predefined_list'),
    path('predefined/<str:set_key>/', views.predefined_set, name='predefined_set'),

    path("quiz/take/", views.take_quiz, name='take_quiz'),
    path("quiz/skip/", views.quiz_skip, name='quiz_skip'),
    path("quiz/finish/", views.quiz_finished, name='quiz_finished'),
    path("quiz/stop/", views.quiz_stop, name='quiz_stop'),
    path("quiz/start/", views.start_quiz, name='quiz_start'),
    path('predefined/<str:set_key>/', views.predefined_set, name='predefined_set'),
    path("predefined/<str:set_key>/quiz/start/", views.pre_quiz_start, name="pre_quiz_start"),
    path("predefined/quiz/take/", views.pre_take_quiz, name="pre_take_quiz"),
    path("predefined/quiz/skip/", views.pre_quiz_skip, name="pre_quiz_skip"),
    path("predefined/quiz/stop/", views.pre_quiz_stop, name="pre_quiz_stop"),
    path("predefined/quiz/finished/", views.pre_quiz_finished, name="pre_quiz_finished"),


]