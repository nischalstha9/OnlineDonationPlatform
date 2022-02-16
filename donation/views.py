import rest_framework
from rest_framework.permissions import IsAuthenticated
from donation.models import Category, Donation
from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from .serializers import CategorySerializer,DonationSerializer
from authentication.permissions import IsAdminPermission, IsDontationOwnerPermission, ReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter


# Create your views here
class CategoryListCreateAPIView(ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAdminPermission|ReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['parent']
    search_fields = ['name']

class DonationListCreateAPIView(ListCreateAPIView):
    serializer_class = DonationSerializer
    queryset = Donation.objects.all()
    permission_classes = [IsAuthenticated|ReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'location', 'active']
    search_fields = ['title', 'category__name', 'location']

class DonationRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = DonationSerializer
    queryset = Donation.objects.all()
    permission_classes = [IsDontationOwnerPermission]
