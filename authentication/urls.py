from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import (
    UserObtainTokenView, CustomerObtainTokenView, BlacklistView, UserView, UserListView, isTokenValid,
    activateAccount, resetPassword, forgetPassword, changePassword, UserDetailView, CustomerListView, CustomerDetailView, CustomerView,
    # HotelUserListView, HotelUserDetailView, HotelUserView, HotelRegisterView, exchange_token
)

urlpatterns = [
    path('user/', UserView.as_view(), name="user"),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('user/all/', UserListView.as_view(), name="all-user"),
    path('user/password/', changePassword, name='change-password'),
    path('token/obtain/', UserObtainTokenView.as_view(), name='token-create'),
    path('customer/token/obtain/', CustomerObtainTokenView.as_view(),
         name='token-create-customer'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token-refresh'),
    path('token/blacklist/', BlacklistView.as_view(), name='token-blacklist'),
    path('token/valid/', isTokenValid, name='token-valid'),
    path('user/activate/', activateAccount, name='user-activate'),
    path('user/reset/', resetPassword, name='user-reset'),
    path('user/forget/', forgetPassword, name='user-forget-password'),
    # path('token/social/<backend>/', exchange_token, name='social-login'),
    path('customer/', CustomerView.as_view(), name="customer"),
    path('customer/all/', CustomerListView.as_view(), name="all-customer"),
    # path('customer/<int:pk>/', CustomerDetailView.as_view(),name="customer-detail"),
    # path('hotel/<slug:slug>/hoteluser/', HotelUserView.as_view(), name="hotel-user"),
    # path('hotel/<slug:slug>/hoteluser/all/', HotelUserListView.as_view(),name="all-hotel-user"),
    # path('hotel/<slug:slug>/hoteluser/<int:pk>/', HotelUserDetailView.as_view(),name="hotel-user-detail"),
    # path('hotel/register/', HotelRegisterView.as_view(),name="hotel-register-detail"),
]
