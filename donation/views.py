from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from donation.models import Category, Donation
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import CategorySerializer,DonationSerializer
from authentication.permissions import IsAdminPermission, IsDontationOwnerOrReadOnlyPermission, ReadOnly, is_user_admin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status


# Create your views here
class CategoryListCreateAPIView(ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAdminPermission|ReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['parent']
    search_fields = ['name']
    ordering_fields = ['name', 'id']
    pagination_classes = [LimitOffsetPagination]

class DonationListCreateAPIView(ListCreateAPIView):
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated|ReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'location', 'active', 'doner']
    search_fields = ['title', 'category__name', 'location']
    ordering_fields = ['title', 'category__name', 'location', 'created_at', 'updated_at']
    pagination_classes = [LimitOffsetPagination]

    def get_queryset(self):
        if(self.request.query_params.get('active')):
            if is_user_admin(self.request):
                return Donation.objects.all()
        return Donation.objects.filter(active=True)

class DonationRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = DonationSerializer
    permission_classes = [IsDontationOwnerOrReadOnlyPermission]
    
    def get_queryset(self):
        return Donation.objects.all()

    def get(self, request, pk, format=None):
        obj = self.get_object()
        if not obj.active:
            if obj.doner != request.user:
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
    pagination_classes = [LimitOffsetPagination]

    def get_queryset(self):
        return Donation.objects.filter(doner=self.request.user)