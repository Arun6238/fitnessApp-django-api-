from django.urls import path
from . import views

urlpatterns = [
    path('add-default-exercise/',views.add_default_exercise),
    path('add-default/',views.addDefault),
    path('exercise-list/',views.exercise_list),
    path('exercise-details/',views.get_exercise),
    path('start-new-training-session/',views.start_new_training_session),
    path('get_all_templates/',views.get_all_templates,),
    path('create_new_template/',views.create_new_template),
    path('delete-template/<int:id>',views.delete_template),
    path('rename-template/<int:id>',views.rename_template),
    path('update-template/<int:id>',views.update_template)
]
# api/exercise/rename-template/<int:id>
