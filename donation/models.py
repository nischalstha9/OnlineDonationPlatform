from django.db import models
from django.utils.translation import ugettext_lazy as _
from authentication.utils import mobile_num_regex_validator

# Create your models here.
class Category(models.Model):
    name = models.CharField(_("Category Name"), max_length=50)
    parent = models.ForeignKey("donation.Category", verbose_name=_("Parent Category"), on_delete=models.CASCADE, null=True, blank=True)    

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name



class Donation(models.Model):
    title = models.CharField(_("Item Name"), max_length=100)
    description = models.TextField(_("Description"), null=False, blank=False)
    category = models.ForeignKey("donation.Category", verbose_name=_("Category"), on_delete=models.SET_NULL, null=True, blank=False)
    location = models.CharField(_("Location"), max_length=100)
    contact  = models.CharField(validators=[mobile_num_regex_validator], max_length=13)
    doner = models.ForeignKey("authentication.CustomUser", verbose_name=_("Doner User"), on_delete=models.CASCADE)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    active = models.BooleanField(_("Is Active"), default=False)

    class Meta:
        verbose_name = _("Donation")
        verbose_name_plural = _("Donations")

    def __str__(self):
        return self.title


