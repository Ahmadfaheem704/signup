# api/urls.py

from django.urls import path
from .views import UserRegistrationView, LoginAPIView, LogoutAPIView, SubscriptionAPIView, VideoListAPIView, PaymentSuccessView

urlpatterns = [
    path('subscribe/', SubscriptionAPIView.as_view(), name='subscribe'),
    path('videos/<str:plan_type>/', VideoListAPIView.as_view(), name='video-list'),
    path('signup/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', LoginAPIView.as_view(), name='user-login'),
    path('logout/', LogoutAPIView.as_view(), name='user-logout'),
    path('success/', PaymentSuccessView.as_view(), name='payment-success'),
]
