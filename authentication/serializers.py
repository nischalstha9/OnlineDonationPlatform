from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import CustomUser, Customer, UserToken

from rest_framework.validators import UniqueValidator

from .utils import RandomStringTokenGenerator
from .tasks import send_register_mail
from datetime import date

from .constants import DEFAULT_ASSETS_IMAGES_PATH, ADMIN_DOMAIN, CLIENT_DOMAIN


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        # Add custom claims
        token['user_id'] = user.id
        token['role'] = user.role
        if user.role == 1:
            token['hotel_slug'] = user.hoteluser.hotel.slug
            token['hotel_id'] = user.hoteluser.hotel.id
        return token


class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserToken
        exclude = ['id']


class CustomUserSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    password = serializers.CharField(min_length=8, write_only=True)
    is_active = serializers.BooleanField(required=False, default=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'date_joined', 'is_active',
                  'email', 'password', 'phone', 'avatar', 'last_login', 'email_verified')
        extra_kwargs = {'password': {'write_only': True}, 'last_login': {
            'read_only': True}, 'email_verified': {'read_only': True}}

    def get_gender(self, obj):
        return obj.get_gender_display()

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        validated_data['role'] = 0
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        from django.conf import settings
        request = self.context.get('request')
        assets_image_path = str(request.build_absolute_uri(
            settings.MEDIA_URL + DEFAULT_ASSETS_IMAGES_PATH))
        domain = ADMIN_DOMAIN
        try:
            send_register_mail(instance, domain, assets_image_path,
                               UserTokenSerializer, 'register-confirm-admin.html')
        except Exception:
            instance.delete()
            raise serializers.ValidationError(
                {"detail": "Error in creating token"})
        return instance

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


# class HotelUserSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(
#         required=True,
#         validators=[UniqueValidator(queryset=CustomUser.objects.all())]
#     )
#     password = serializers.CharField(min_length=8, write_only=True)
#     is_active = serializers.BooleanField(required=False, default=True)

#     class Meta:
#         model = HotelUser
#         fields = ('id', 'first_name', 'last_name', 'date_joined', 'is_active', 'email',
#                   'password', 'phone', 'avatar', 'last_login', 'email_verified', 'hotel')
#         extra_kwargs = {'password': {'write_only': True}, 'hotel': {
#             'write_only': True}, 'last_login': {'read_only': True}, 'email_verified': {'read_only': True}}

#     def get_gender(self, obj):
#         return obj.get_gender_display()

#     def create(self, validated_data):
#         password = validated_data.pop('password', None)
#         instance = self.Meta.model(**validated_data)
#         if password is not None:
#             instance.set_password(password)
#         instance.save()
#         from django.conf import settings
#         request = self.context.get('request')
#         assets_image_path = str(request.build_absolute_uri(
#             settings.MEDIA_URL + DEFAULT_ASSETS_IMAGES_PATH))
#         domain = ADMIN_DOMAIN
#         try:
#             send_register_mail(instance, domain, assets_image_path,
#                                UserTokenSerializer, 'register-confirm.html')
#         except Exception:
#             instance.delete()
#             raise serializers.ValidationError(
#                 {"detail": "Error in creating token"})
#         return instance

#     def update(self, instance, validated_data):
#         return super().update(instance, validated_data)


class CustomerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=CustomUser.objects.all()),
        ]
    )
    password = serializers.CharField(min_length=8, write_only=True)
    is_active = serializers.BooleanField(required=False, default=True)
    email_verified = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Customer
        fields = ('id', 'first_name', 'last_name', 'date_joined', 'is_active', 'email',
                  'password', 'gender', 'phone', 'avatar', 'last_login', 'dob', 'email_verified')
        extra_kwargs = {'password': {'write_only': True}, 'is_staff': {'write_only': True},
                        'last_login': {'read_only': True}, 'email_verified': {'read_only': True}}

    def validate_dob(self, value):
        dob = value
        today = date.today()
        if (dob.year + 7, dob.month, dob.day) > (today.year, today.month, today.day):
            raise serializers.ValidationError(
                'Must be at least 7 years old to register')
        return dob

    def get_gender(self, obj):
        return obj.get_gender_display()

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        try:
            from django.conf import settings
            request = self.context.get('request')
            assets_image_path = str(request.build_absolute_uri(
                settings.MEDIA_URL + DEFAULT_ASSETS_IMAGES_PATH))
            domain = CLIENT_DOMAIN
            send_register_mail(instance, domain, assets_image_path,
                               UserTokenSerializer, 'register-confirm-admin.html')
        except Exception:
            instance.delete()
            raise serializers.ValidationError(
                {"detail": "Error in creating token"})
        return instance

    def update(self, instance, validated_data):
        if('password' in [x for x in validated_data]):
            validated_data.pop('password')
        return super().update(instance, validated_data)


class PasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
