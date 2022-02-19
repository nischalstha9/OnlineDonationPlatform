from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

# Create your models here.
class Comment(models.Model):
    text = models.CharField(_("Comment Text"), max_length=200)
    content = models.ForeignKey(ContentType, verbose_name=_("Content"), on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, verbose_name=_("Content Type of Post"), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("Comment_detail", kwargs={"pk": self.pk})
