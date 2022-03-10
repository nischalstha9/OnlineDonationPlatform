from datetime import timedelta, datetime
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from donation.models import Category, Donation
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import CategorySerializer,DonationSerializer
from authentication.permissions import IsAdminPermission, IsDontationOwnerOrReadOnlyPermission, ReadOnly, is_user_admin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from authentication.models import Customer
from django.db.models import Count

# Create your views here
class CategoryListCreateAPIView(ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().annotate(num_donations = Count("donations")).order_by('-num_donations')
    permission_classes = [IsAdminPermission|ReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['parent']
    search_fields = ['name']
    ordering_fields = ['name', 'id']
    pagination_class = LimitOffsetPagination

class DonationListCreateAPIView(ListCreateAPIView):
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated|ReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'location', 'active', 'user']
    search_fields = ['title', 'category__name', 'location']
    ordering_fields = ['title', 'category__name', 'location', 'created_at', 'updated_at']
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        if(self.request.query_params.get('active')):
            if is_user_admin(self.request):
                return Donation.objects.all().prefetch_related("likes").select_related("category", "user")
        return Donation.objects.filter(active=True).prefetch_related("likes").select_related("category", "user")

class DonationRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = DonationSerializer
    permission_classes = [IsDontationOwnerOrReadOnlyPermission]
    lookup_field = "slug"
    lookup_url_kwarg = "help_slug"
    
    def get_queryset(self):
        return Donation.objects.all().select_related("category", "user").prefetch_related("likes")

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.active:
            if obj.user != request.user:
                return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        serializer = DonationSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MyDonationListView(ListAPIView):
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'location', 'active']
    search_fields = ['title', 'category__name', 'location']
    ordering_fields = ['title', 'category__name', 'location', 'created_at', 'updated_at']
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Donation.objects.filter(user=self.request.user).select_related("category", "user").prefetch_related("likes")


class MetaImageListCreateSerializer(ListCreateAPIView):
    pass

class HomePageMeta(APIView):
    def get(self, request, *args, **kwargs):
        top_doners = Customer.objects.values('id', "first_name","last_name","email").annotate(num_donations=Count('donations')).order_by('-num_donations')[:10]
        all_categories = Category.objects.values("id","name","parent")
        top_categories = all_categories.annotate(num_donations = Count("donations")).order_by('-num_donations')[:10]
        total_donations = Donation.objects.count()
        total_active_donations = Donation.objects.filter(active=True).count()
        donations_24 = Donation.objects.filter(created_at__gte=datetime.now().astimezone()-timedelta(hours=24)).values("id","title")
        data = {
            "top_doners":top_doners,
            "all_categories": all_categories,
            "top_categories":top_categories,
            "total_donations":total_donations,
            "total_active_donations":total_active_donations,
            "donations_24":donations_24,
            }
        return Response(data,status=200)
    

class DonationLikeToggleView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self, request, *args, **kwargs):
        donation_id = kwargs.get("donation_id")
        donation = Donation.objects.get(pk = donation_id)
        user = request.user
        liked = donation.likes.filter(pk=user.pk).exists()
        if liked:
            donation.likes.remove(self.request.user)
        else:
            donation.likes.add(self.request.user)
        return Response({"liked":not liked}, status = status.HTTP_202_ACCEPTED)