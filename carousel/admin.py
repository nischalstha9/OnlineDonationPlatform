from django.contrib import admin
from .models import *

# Register your models here.
class CarouselImageInline(admin.TabularInline):
    model = CarouselImage

class CarouselAdmin(admin.ModelAdmin):
    inlines=[
        CarouselImageInline
    ]
    pass
admin.site.register(Carousel, CarouselAdmin)
