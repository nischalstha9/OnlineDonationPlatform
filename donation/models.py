from PIL import Image
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from authentication.utils import mobile_num_regex_validator
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify

# Create your models here.
class Category(models.Model):
    name = models.CharField(_("Category Name"), max_length=50, unique=True)
    parent = models.ForeignKey("donation.Category", verbose_name=_("Parent Category"), on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

    def get_content_type(self):
        return ContentType.objects.get_for_model(self.__class__)


class DonationLikes(models.Model):
    donation = models.ForeignKey("donation.Donation", verbose_name=_("Donation"), on_delete=models.CASCADE)
    user = models.ForeignKey("authentication.CustomUser", verbose_name=_("User"), on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now())

    def __str__(self) -> str:
        return f"{str(self.created_at)}-{self.user.email} - {self.donation.title}"

    class Meta:
        auto_created=True
        db_table = "donation_donationlikes"

class Donation(models.Model):
    title = models.CharField(_("Item Name"), max_length=100)
    description = models.TextField(_("Description"), null=False, blank=False)
    category = models.ForeignKey("donation.Category", verbose_name=_("Category"), on_delete=models.SET_NULL, null=True, blank=False, related_name='donations' )
    location = models.CharField(_("Location"), max_length=100)
    contact  = models.CharField(validators=[mobile_num_regex_validator], max_length=13)
    user = models.ForeignKey("authentication.CustomUser", verbose_name=_("Doner User"), on_delete=models.CASCADE, related_name='donations')
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    active = models.BooleanField(_("Is Active"), default=False)
    slug = models.SlugField(_("Slug"), blank=True, null=False)
    likes = models.ManyToManyField("authentication.CustomUser", verbose_name=_("Likers"), through='DonationLikes', related_name="donation_obj", blank=True)

    class Meta:
        verbose_name = _("Donation")
        verbose_name_plural = _("Donations")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("DonationRetrieveUpdateDestroyAPIView", kwargs={"pk": self.pk})

    def get_content_type(self):
        return ContentType.objects.get_for_model(self.__class__)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.title)
            qs = Donation.objects.filter(slug = slug)
            if qs.exists():
                slug = slug + f"-{qs.last().id}"
            self.slug = slug
        super(Donation,self).save(*args, **kwargs)
   
class MetaImage(models.Model):
    image = models.ImageField(_("Image"), upload_to="meta-images/", null=False, blank=False)
    text = models.CharField(_("Comment Text"), max_length=200, blank=True, null=True)
    user = models.ForeignKey("authentication.CustomUser", verbose_name=_("Uploader"), on_delete=models.CASCADE)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("MetaImage")
        verbose_name_plural = _("MetaImages")

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse("MetaImage_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        super(MetaImage,self).save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)
            if img.height > 1200 or img.width > 1200:
                output_size = (1200, 1200)
                img.thumbnail(output_size)
                img.save(self.image.path)


    

