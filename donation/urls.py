from django.urls import path
from .views import CategoryListCreateAPIView, DonationLikeToggleView, DonationListCreateAPIView, DonationRetrieveUpdateDestroyAPIView, HomePageMeta, LikedDonationListView, UserDonationListView, MyDonationListView,RelatedDonationListAPIView

urlpatterns = [
    path('category/', CategoryListCreateAPIView.as_view(), name="CategoryListCreateAPIView"),
    path('donation/', DonationListCreateAPIView.as_view(), name="DonationListCreateAPIView"),
    path('donation/<slug:help_slug>/', DonationRetrieveUpdateDestroyAPIView.as_view(), name="DonationRetrieveUpdateDestroyAPIView"),
    path('donation/<int:donation_id>/like/', DonationLikeToggleView.as_view(), name="DonationLikeToggleView"),
    path('my-donations/', MyDonationListView.as_view(), name="MyDonationListView"),
    path('user-donations/<int:user_id>/', UserDonationListView.as_view(), name="UserDonationListAPIView"),
    path('liked-donations/', LikedDonationListView.as_view(), name="LikedDonationListAPIView"),
    path('home-meta/', HomePageMeta.as_view(), name="HomepageMeta"),
    path('get-related-helps/', RelatedDonationListAPIView.as_view(), name="GetRelatedHelps"),
]
