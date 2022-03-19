from carousel.serializers import CarouselDetailSerializer
from django.shortcuts import render
from rest_framework.generics import RetrieveAPIView
from .models import Carousel, CarouselImage

# Create your views here.
class CarouselRetrieveAPIView(RetrieveAPIView):
    model = Carousel
    queryset = Carousel.objects.all().prefetch_related("carousel_images")
    serializer_class = CarouselDetailSerializer

