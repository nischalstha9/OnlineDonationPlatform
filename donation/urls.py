from django.urls import path
from .views import CategoryListCreateAPIView, DonationLikeToggleView, DonationListCreateAPIView, DonationRetrieveUpdateDestroyAPIView, HomePageMeta, LikedDonationListView, MyDonationListView

urlpatterns = [
    path('category/', CategoryListCreateAPIView.as_view(), name="CategoryListCreateAPIView"),
    path('donation/', DonationListCreateAPIView.as_view(), name="DonationListCreateAPIView"),
    path('donation/<slug:help_slug>/', DonationRetrieveUpdateDestroyAPIView.as_view(), name="DonationRetrieveUpdateDestroyAPIView"),
    path('donation/<int:donation_id>/like/', DonationLikeToggleView.as_view(), name="DonationLikeToggleView"),
    path('mydonations/', MyDonationListView.as_view(), name="MyDonationListAPIView"),
    path('liked-donations/', LikedDonationListView.as_view(), name="LikedDonationListAPIView"),
    path('home-meta/', HomePageMeta.as_view(), name="HomepageMeta"),
]
