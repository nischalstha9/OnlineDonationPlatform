from rest_framework import permissions
from .models import CustomUser
# from hotel.models import Hotel


def is_user_customer_or_anonym(request):
    if request.user.is_authenticated:
        return request.user.role == 2
    else:
        return True


def is_user_customer(request):
    if request.user.is_authenticated:
        return request.user.role == 2
    else:
        return False


def is_user_hotel_user(request):
    if request.user.is_authenticated:
        return request.user.role == 1
    else:
        return False


class IsCustomerOrAnonymPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return is_user_customer_or_anonym(request)


class OwnProfilePermissionUrl(permissions.BasePermission):

    def has_permission(self, request, view):
        user = CustomUser.objects.get(pk=view.kwargs['pk'])

        if request.user == user:
            return True
        else:
            return False


class OnlyAdminPostPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.method == 'POST' and request.user.role != 0:
                return False
            else:
                return True
        return False


class OnlyAdminOrHotelUserChangePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        if request.user.is_authenticated:
            if (request.method in ['POST', 'PATCH', 'PUT', 'DELETE']) and request.user.role in [0, 1]:
                return True
            else:
                return False
        return False


class IsAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 0:
            return True
        return False


class IsAdminOrHotelUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and (request.user.role == 0 or request.user.role == 1):
            return True
        return False


class IsHotelUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 1:
            return True
        return False


class IsCustomerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if(request.user.is_authenticated and request.user.role == 2):
            return True
        return False


class IsAdminOrHotelOwnerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            slug = view.kwargs.get('slug', None)
            hotel = Hotel.objects.get(slug=slug)
            if request.user.role == 0 or (request.user.role == 1 and request.user.hoteluser.hotel == hotel):
                return True
            return False
        except Exception:
            return False
