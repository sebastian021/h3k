from . views import RegisterView, CustomTokenObtainPairView, LoginAPIView, LogoutAPIView
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/',RegisterView.as_view(),name="register"),
    path('loogin/', LoginAPIView.as_view(),name="loogin"),
    path('login/', CustomTokenObtainPairView.as_view(),name="login"),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]