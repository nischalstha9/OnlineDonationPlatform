from django.db import models
from django.utils.translation import gettext_lazy as _
from PIL import Image

# Create your models here.

class Carousel(models.Model):
    name = models.CharField(_("Carousel Name"), max_length=50)

    class Meta:
        verbose_name = _("Carousel")
        verbose_name_plural = _("Carousels")

    def __str__(self):
        return self.name


class CarouselImage(models.Model):
    carousel = models.ForeignKey("carousel.Carousel", verbose_name=_("Carousel"), on_delete=models.CASCADE, related_name="carousel_images")
    image = models.ImageField(_("Image"), upload_to="carousel/", blank=False, null=False)
    caption = models.CharField(_("Caption"), max_length=50)
    position = models.IntegerField(_("Position"), null=True, blank=True)

    class Meta:
        verbose_name = _("CarouselImage")
        verbose_name_plural = _("CarouselImages")
        unique_together=[("carousel","position")]

    def __str__(self):
        return self.carousel.name

    def save(self, *args, **kwargs):
        super(CarouselImage,self).save(*args, **kwargs)
        img = Image.open(self.image.path)
        threshold=1920
        if img.height > threshold or img.width > threshold:
            output_size = (threshold, threshold)
            img.thumbnail(output_size)
            img.save(self.image.path)

