from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from donation.models import Category, Donation, MetaImage
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import CategorySerializer,DonationSerializer, MetaImageListCreateSerializer
from authentication.permissions import IsAdminPermission, IsDontationOwnerOrReadOnlyPermission, ReadOnly, is_user_admin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from django.db.models import Count, Q, Case, Value, When


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
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
        ]
    filterset_fields = ['category', 'location', 'active', 'user']
    search_fields = ['title', 'category__name', 'location']
    ordering_fields = [
        'title',
        'category__name',
        'location',
        'created_at',
        'updated_at'
        ]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        if(self.request.query_params.get('active')):
            if is_user_admin(self.request):
                return Donation.objects.all()\
                .prefetch_related("likes").select_related("category", "user")
        return Donation.objects.filter(active=True)\
        .prefetch_related("likes").select_related("category", "user")

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

class UserDonationListView(ListAPIView):
    serializer_class = DonationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'location']
    search_fields = ['title', 'category__name', 'location']
    ordering_fields = ['title', 'category__name', 'location', 'created_at', 'updated_at']
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        return Donation.objects.filter(user__id=user_id, active=True).select_related("category", "user").prefetch_related("likes")

class MyDonationListView(UserDonationListView):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'location', 'active']

    def get_queryset(self):
        return Donation.objects.filter(user=self.request.user).select_related("category", "user").prefetch_related("likes")


class LikedDonationListView(ListAPIView):
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'location']
    search_fields = ['title', 'category__name', 'location']
    # ordering_fields = ['title', 'category__name', 'location', 'created_at', 'updated_at']
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        qs = Donation.objects.filter(likes=self.request.user).order_by("-donationlikes__id").select_related("user","category")
        return qs
    

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     # queryset = [i.donation for i in queryset]
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = DonationSerializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = DonationSerializer(queryset, many=True)
    #     return Response(serializer.data)
    
    # def get(self, request, *args, **kwargs):
    #     qs = DonationLikes.objects.filter(user=self.request.user).select_related("donation","donation__user","donation__category")
    #     qs = [i.donation for i in qs]
    #     paginated_qs = self.paginate_queryset(qs)
    #     data = DonationSerializer(paginated_qs, many=True).data
    #     resp = self.get_paginated_response(data)
    #     return resp
        # page = self.paginate_queryset(qs)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        # serializer = self.get_serializer(queryset, many=True)
        # return Response(serializer.data)
        

class HomePageMeta(APIView):
    def get(self, request, *args, **kwargs):
        # top_doners = Customer.objects.values('id', "first_name","last_name","email").annotate(num_donations=Count('donations')).order_by('-num_donations')[:10]
        all_categories_qs = Category.objects.all().select_related("parent").annotate(num_donations = Count("donations",filter=Q(donations__active=True))).order_by("id")
        all_categories = CategorySerializer(all_categories_qs, many=True).data
        # total_donations = Donation.objects.count()
        # total_active_donations = Donation.objects.filter(active=True).count()
        # donations_24 = Donation.objects.filter(created_at__gte=datetime.now().astimezone()-timedelta(hours=24)).values("id","title")
        most_liked_donations_qs = Donation.objects.filter(active=True).annotate(num_likes=Count("likes")).order_by("-num_likes").select_related("user").prefetch_related("likes").values("id","title","slug","num_likes","updated_at","user__first_name","user__last_name","user__avatar")[:5]
        # most_liked_donations = DonationSerializer(most_liked_donations_qs, many=True).data
        data = {
            # "top_doners":top_doners,
            "all_categories": all_categories,
            # "top_categories":top_categories,
            "most_liked_donations":most_liked_donations_qs,
            # "total_donations":total_donations,
            # "total_active_donations":total_active_donations,
            # "donations_24":donations_24,
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

class RelatedDonationListAPIView(ListAPIView):
    serializer_class = DonationSerializer
    # filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['category', 'location', 'active', 'user']
    # search_fields = ['title', 'category__name', 'location']
    # ordering_fields = ['title', 'category__name', 'location', 'created_at', 'updated_at']
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        try:
            help_id = self.request.GET.get('help_id')
            help_obj = Donation.objects.get(id=help_id)
            category = help_obj.category
            location = help_obj.location[:5]
            user = help_obj.user
            # updated_at = help_obj.updated_at
            # date_start_range = updated_at-timedelta(days=1)
            # date_end_range = updated_at+timedelta(days=1)
            qs = Donation.objects.exclude(id=help_id).filter(active=True) \
                .filter(
                    Q(category=category)|
                    Q(location__icontains=location)|
                    Q(user=user)
                    ).select_related("category", "user").prefetch_related("likes").distinct()
            # if qs.count() < 1:
            #     new_qs = Donation.objects.exclude(id=help_id).filter(active=True).filter(
            #         Q(updated_at__gte=date_start_range)|
            #         Q(updated_at__lte=date_end_range)
            #     ).select_related("category", "user").prefetch_related("likes").distinct()
            #     qs = qs.union(new_qs)
            return qs[:9]
        except Exception:
            return Donation.objects.none()

class MetaImageListCreateAPIView(ListCreateAPIView):
    serializer_class = MetaImageListCreateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user','created_at']
    search_fields = ['text']
    ordering_fields = ['text', 'id','created_at']
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return MetaImage.objects.filter(user=self.request.user)