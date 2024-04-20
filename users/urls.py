from . views import RegisterView, CustomTokenObtainPairView, LogoutAPIView
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/',RegisterView.as_view(),name="register"),
    path('login/', CustomTokenObtainPairView.as_view(),name="login"),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]