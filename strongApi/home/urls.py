from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('login-user/',views.login_user,name='login-user'),
    path('logout-user/',views.logout_user),
    path('register-user/',views.register_user,name="register-user"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/refresh/both',views.get_tokens_for_user,name='refresh_both'),
    path('token/check/',views.is_user_loggedin),
]

