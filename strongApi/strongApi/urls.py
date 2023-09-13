from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include('home.urls')),
    path('api/exercise/',include('exercise.urls')),
]
