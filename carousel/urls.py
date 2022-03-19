from django.urls import path
from .views import CarouselRetrieveAPIView

urlpatterns = [
    path('<int:pk>/detail/', CarouselRetrieveAPIView.as_view(), name="CarouselRetrieveAPIView"),
]
