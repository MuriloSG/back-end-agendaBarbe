from django.urls import path

from users.views import (
    BarberListView, 
    UserLoginView, 
    UserLogoutView, 
    UserProfileView, 
    UserRegistrationView, 
    RatingView,
    PasswordResetRequestView,
    PasswordResetConfirmView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('barbers/', BarberListView.as_view(), name='barber-list'),
    path('ratings/', RatingView.as_view(), name='rating'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
