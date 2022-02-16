from django.urls import path
from .views import CategoryListCreateAPIView, DonationListCreateAPIView, DonationRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('category/', CategoryListCreateAPIView.as_view(), name="CategoryListCreateAPIView"),
    path('donation/', DonationListCreateAPIView.as_view(), name="DonationListCreateAPIView"),
    path('donation/<int:pk>/', DonationRetrieveUpdateDestroyAPIView.as_view(), name="DonationRetrieveUpdateDestroyAPIView"),
]
