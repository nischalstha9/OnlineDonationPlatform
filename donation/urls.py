from django.urls import path
from .views import CategoryListCreateAPIView, DonationListCreateAPIView, DonationRetrieveUpdateDestroyAPIView, MyDonationListView

urlpatterns = [
    path('category/', CategoryListCreateAPIView.as_view(), name="CategoryListCreateAPIView"),
    path('donation/', DonationListCreateAPIView.as_view(), name="DonationListCreateAPIView"),
    path('donation/<int:pk>/', DonationRetrieveUpdateDestroyAPIView.as_view(), name="DonationRetrieveUpdateDestroyAPIView"),
    path('donation/mydonations/', MyDonationListView.as_view(), name="MyDonationListAPIView"),
]
