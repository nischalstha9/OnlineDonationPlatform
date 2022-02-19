from donation.models import Donation
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey


class CommentManager(models.Manager):
    def filter_by_instance(self,instance):
        content_type = ContentType.objects.get_for_model(instance.__class__)
        obj_id = instance.id
        qs = super(CommentManager, self).filter(content_type=content_type, object_id=obj_id)
        return qs

# Create your models here.
class Comment(models.Model):
    text = models.CharField(_("Comment Text"), max_length=200)
    user = models.ForeignKey("authentication.CustomUser", verbose_name=_("Commenter"), on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, verbose_name=_("Content Type of Post"), on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(_("Post Object Id"))
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    objects = CommentManager()

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("Comment_detail", kwargs={"pk": self.pk})
