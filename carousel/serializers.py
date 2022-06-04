from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Carousel, CarouselImage

class CarouseImageSerializer(ModelSerializer):
    class Meta:
        model = CarouselImage
        fields = "__all__"

class CarouselDetailSerializer(ModelSerializer):
    carousel_images = SerializerMethodField()
    class Meta:
        model = Carousel
        fields = "__all__"

    def get_carousel_images(self, obj):
        return CarouseImageSerializer(obj.carousel_images.all().order_by("-position"), many=True).data