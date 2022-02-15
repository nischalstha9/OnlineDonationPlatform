# from django.db import models
# from .default_models import CustomUser
# # from hotel.models import Hotel
# from authentication.managers import HotelUserManager


# class HotelUser(CustomUser):
#     objects = HotelUserManager()
#     hotel = models.ForeignKey(to=Hotel, related_name='hotel_user', on_delete=models.CASCADE)

#     class Meta:
#         verbose_name_plural = "hotelusers"

#     def save(self, *args, **kwargs):
#         self.role = 1
#         self.is_staff = False
#         self.is_superuser = False

#         super(HotelUser,self).save(*args, **kwargs)
