from django.urls import path
from . import views

urlpatterns = [
    path('add-default-exercise/',views.add_default_exercise),
    path('add-default/',views.addDefault),
    path('exercise-list/',views.exercise_list)
]

