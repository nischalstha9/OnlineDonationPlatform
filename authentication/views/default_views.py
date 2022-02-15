from rest_framework_simplejwt.views import TokenObtainPairView
from authentication.serializers import MyTokenObtainPairSerializer, CustomUserSerializer, PasswordSerializer, CustomerSerializer, UserTokenSerializer
from rest_framework.response import Response
from rest_framework import status, permissions
from authentication.models import Customer, CustomUser, UserToken
from authentication.permissions import IsAdminPermission, IsAdminOrHotelUserPermission, IsAdminOrHotelOwnerPermission
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework import filters
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
# from hotel.models import Hotel, Popularity

from authentication.utils import RandomStringTokenGenerator

from authentication.constants import DEFAULT_ASSETS_IMAGES_PATH, ADMIN_DOMAIN, CLIENT_DOMAIN

from django.template.loader import render_to_string

from rest_framework.generics import (
    ListAPIView, RetrieveUpdateDestroyAPIView,
)


def get_user_verification(data):
    try:
        email = data['email']
        user = CustomUser.users.get(email=email)
        if user:
            if not user.email_verified:
                return status.HTTP_406_NOT_ACCEPTABLE
        return None
    except Exception:
        return None


class UserObtainTokenView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        request.PAYLOAD_SOURCE = 'User'
        if(get_user_verification(request.data) == status.HTTP_406_NOT_ACCEPTABLE):
            return Response({"detail": "Inactive user. Please activate from email or contact us for support"}, status.HTTP_401_UNAUTHORIZED)
        return super().post(request, *args, **kwargs)


class CustomerObtainTokenView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class BlacklistView(APIView):

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserListView(ListAPIView):
    permission_classes = [IsAdminPermission]
    search_fields = ['first_name', 'last_name', 'email']
    filter_backends = (filters.SearchFilter,)
    queryset = CustomUser.users.all()
    serializer_class = CustomUserSerializer


class UserDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminPermission]
    queryset = CustomUser.users.all()
    serializer_class = CustomUserSerializer


class UserView(APIView):
    permission_classes = [IsAdminPermission]

    def get(self, request):
        try:
            serializer = CustomUserSerializer(request.user)
            return Response(serializer.data)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, format=None):
        serializer = CustomUserSerializer(
            request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, format='json'):
        try:
            serializer = CustomUserSerializer(
                data=request.data, context={"request": request})
            if serializer.is_valid():
                user = serializer.save()
                if user:
                    json = serializer.data
                    return Response(json, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except serializers.ValidationError as err:
            return Response(err.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exe:
            return Response({"detail": "Error creating user", "error": str(exe)}, status=status.HTTP_400_BAD_REQUEST)


def validate_password_strength(value):
    """Validates that a password is as least 8 characters long and has at least
    1 digit and 1 letter.
    """
    min_length = 8

    if len(value) < min_length:
        raise Exception(
            f'Password must contain at least {min_length} characters with minimum 1 digit and 1 character.')

    # check for digit
    if not any(char.isdigit() for char in value):
        raise Exception(
            f'Password must contain at least {min_length} characters with minimum 1 digit and 1 character.')

    # check for letter
    if not any(char.isalpha() for char in value):
        raise Exception(
            f'Password must contain at least {min_length} characters with minimum 1 digit and 1 character.')


@api_view(['PUT'])
def changePassword(request):
    try:
        user = request.user
        data = request.data
        serializer = PasswordSerializer(data=data)
        if serializer.is_valid():
            if user.check_password(serializer.data.get('old_password')):
                try:
                    validate_password_strength(data['new_password'])
                except Exception as val:
                    return Response({"detail": str(val)}, status=status.HTTP_400_BAD_REQUEST)
                user.set_password(data['new_password'])
                user.save()
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"detail": "Old password does not match!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Error in json format!"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({"detail": "Error in function"}, status=status.HTTP_400_BAD_REQUEST)


def checkValidity(data):
    if(data and 'identifier' in data and 'token' in data and 'type' in data):
        user = CustomUser.objects.filter(id=data['identifier'])
        if (user.last() == None):
            return ({"detail": "User not found"}, status.HTTP_404_NOT_FOUND)
        token = UserToken.objects.filter(
            user=user.last().id, key=data['token'])
        if (token.last() == None):
            return ({"detail": "Token not found"}, status.HTTP_404_NOT_FOUND)
        if(not token.last().isValid()):
            token.last().delete()
            return ({"detail": "Token expires"}, status.HTTP_400_BAD_REQUEST)
        if(token.last().key_type != int(data['type'])):
            return ({"detail": "Token type is not valid"}, status.HTTP_400_BAD_REQUEST)
        return ({"detail": "valid"}, status.HTTP_200_OK)
    else:
        return ({"detail": "Token and identifier needed"}, status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def isTokenValid(request):
    try:
        data = request.data
        msg, statusID = checkValidity(data)
        return Response(msg, statusID)
    except Exception as ex:
        return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def activateAccount(request):
    try:
        data = request.data
        msg, statusID = checkValidity(data)
        if(statusID == status.HTTP_200_OK):
            if(not data['type'] == '0'):
                return Response({"detail": "Token type is not valid"}, status.HTTP_400_BAD_REQUEST)
            user = CustomUser.objects.filter(id=data['identifier']).last()
            user.email_verified = True
            user.save()
            token = UserToken.objects.filter(
                user=user.id, key=data['token']).last()
            token.delete()
            msg["detail"] = "Account activated"
        return Response(msg, statusID)
    except Exception as ex:
        return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def resetPassword(request):
    try:
        data = request.data
        msg, statusID = checkValidity(data)
        if(statusID == status.HTTP_200_OK):
            if(not 'new_password' in data):
                return Response({"detail": "New password not provided"}, status.HTTP_404_NOT_FOUND)
            if(not data['type'] == '1'):
                return Response({"detail": "Token type is not valid"}, status.HTTP_400_BAD_REQUEST)
            user = CustomUser.objects.filter(id=data['identifier']).last()
            try:
                validate_password_strength(data['new_password'])
            except Exception as val:
                return Response({"detail": str(val)}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(data['new_password'])
            user.save()
            token = UserToken.objects.filter(
                user=user.id, key=data['token']).last()
            token.delete()
            msg["detail"] = "Password changed"
        return Response(msg, statusID)
    except Exception as ex:
        return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def forgetPassword(request):
    try:
        data = request.data
        if(data and 'email' in data):
            user = CustomUser.objects.filter(email=data['email'])
            if(user.first() == None):
                return Response({"detail": "User not found"}, status.HTTP_404_NOT_FOUND)
            userInstance = user.first()
            token = UserToken.objects.filter(
                user=userInstance.id, key_type='1').order_by('-created_at')
            if(not token.first() == None):
                latestToken = token.first()
                if(latestToken.isValid()):
                    return Response({"detail": "Token already generated in last 1 hour. Please check your email."}, status.HTTP_400_BAD_REQUEST)
                else:
                    for tok in token:
                        if not tok.isValid():
                            tok.delete()
            rand = RandomStringTokenGenerator()
            token = rand.generate_unique_token(model=UserToken, field="key")
            first_name = userInstance.first_name if (
                len(userInstance.first_name) >= 1) else "User"
            from django.conf import settings
            assets_image_path = str(request.build_absolute_uri(
                settings.MEDIA_URL + DEFAULT_ASSETS_IMAGES_PATH))
            client_domain = CLIENT_DOMAIN
            domain = ADMIN_DOMAIN
            if userInstance.role == 2:
                domain = CLIENT_DOMAIN
            message = render_to_string('forget-password.html',
                                       {'username': first_name, 'domain': domain, 'client_domain': client_domain, 'token': token, 'identifier': userInstance.id, 'url': assets_image_path})
            mail = userInstance.send_mail(
                subject="Microstay - Forget Password", message=message)
            if(mail == "success"):
                data = {"user": userInstance.id, "key": token, "key_type": 1}
                tokenSerializer = UserTokenSerializer(data=data)
                if(tokenSerializer.is_valid(raise_exception=True)):
                    UserToken.objects.create(**tokenSerializer.validated_data)
                return Response({"detail": "Email sent"}, status.HTTP_200_OK)
            else:
                return Response({"detail": "Problem in sending email"}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Email address needed"}, status.HTTP_404_NOT_FOUND)
    except Exception as ex:
        return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)


class CustomerView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            instance = Customer.objects.filter(pk=request.user.id).last()
            if instance is not None:
                serializer = CustomerSerializer(instance)
                return Response(serializer.data)
            else:
                return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, format=None):
        try:
            instance = Customer.objects.filter(pk=request.user.id).last()
            serializer = CustomerSerializer(
                instance, data=request.data, partial=True)
            if(serializer.is_valid(raise_exception=True)):
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except serializers.ValidationError as ex:
            return Response(ex.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({"detail": ex}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format='json'):
        try:
            serializer = CustomerSerializer(
                data=request.data, context={"request": request})
            if serializer.is_valid():
                user = serializer.save()
                if user:
                    json = serializer.data
                    return Response(json, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except serializers.ValidationError as err:
            return Response(err.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"detail": "Error creating customer"}, status=status.HTTP_400_BAD_REQUEST)


class CustomerListView(ListAPIView):
    permission_classes = [IsAdminPermission]
    search_fields = ['first_name', 'last_name', 'email']
    filter_backends = (filters.SearchFilter,)
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class CustomerDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminPermission]
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


# class HotelUserView(APIView):
#     permission_classes = [IsAdminOrHotelUserPermission]

#     def get(self, request, *args, **kwargs):
#         if request.user.role == 0:
#             return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
#         try:
#             instance = HotelUser.objects.filter(pk=request.user.id).last()
#             if instance is not None:
#                 serializer = HotelUserSerializer(instance)
#                 return Response(serializer.data)
#             else:
#                 return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
#         except Exception:
#             return Response(status=status.HTTP_400_BAD_REQUEST)

#     def patch(self, request, *args, **kwargs):
#         if request.user.role == 0:
#             return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
#         try:
#             instance = HotelUser.objects.filter(pk=request.user.id).last()
#             serializer = HotelUserSerializer(
#                 instance, data=request.data, partial=True)
#             if(serializer.is_valid(raise_exception=True)):
#                 serializer.save()
#                 return Response(serializer.data)
#             else:
#                 return Response(status=status.HTTP_400_BAD_REQUEST)
#         except serializers.ValidationError as ex:
#             return Response(ex.detail, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as ex:
#             return Response({"detail": ex}, status=status.HTTP_400_BAD_REQUEST)

#     def post(self, request, *args, **kwargs):
#         try:
#             slug = self.kwargs.get('slug', None)
#             hotel = Hotel.objects.get(slug=slug)
#             if not (request.user.role == 0 or (request.user.role == 1 and request.user.hoteluser.hotel == hotel)):
#                 return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
#             data = request.data.copy()
#             data['hotel'] = hotel.id
#             serializer = HotelUserSerializer(
#                 data=data, context={"request": request})
#             if serializer.is_valid():
#                 user = serializer.save()
#                 if user:
#                     json = serializer.data
#                     return Response(json, status=status.HTTP_201_CREATED)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except serializers.ValidationError as err:
#             return Response(err.detail, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as exp:
#             print(exp)
#             return Response({"detail": "Error creating staff"}, status=status.HTTP_400_BAD_REQUEST)


# class HotelUserListView(ListAPIView):
#     permission_classes = [IsAdminOrHotelOwnerPermission]
#     search_fields = ['first_name', 'last_name', 'email']
#     filter_backends = (filters.SearchFilter,)
#     serializer_class = HotelUserSerializer

#     def get_queryset(self):
#         slug = self.kwargs.get('slug', None)
#         return HotelUser.objects.filter(hotel__slug=slug)


# class HotelUserDetailView(RetrieveUpdateDestroyAPIView):
#     permission_classes = [IsAdminOrHotelOwnerPermission]
#     serializer_class = HotelUserSerializer

#     def get_queryset(self):
#         slug = self.kwargs.get('slug', None)
#         return HotelUser.objects.filter(hotel__slug=slug)


# class HotelRegisterView(APIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request, format='json'):
#         try:
#             hotelSerializer = HVHotelSerializer(
#                 data=request.data, context={"request": request})
#             if hotelSerializer.is_valid():
#                 hotel = hotelSerializer.save()
#                 if hotel:
#                     pop = Popularity.objects.create(hotel=hotel)
#                     data = request.data.copy()
#                     data['hotel'] = hotel.id
#                     serializer = HotelUserSerializer(
#                         data=data, context={"request": request})
#                     if serializer.is_valid():
#                         user = serializer.save()
#                         if user:
#                             json = serializer.data
#                             return Response(json, status=status.HTTP_201_CREATED)
#                     hotel.delete()
#                     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#                 else:
#                     return Response({"detail": "Error creating hotel"}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 return Response(hotelSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except serializers.ValidationError as err:
#             return Response(err.detail, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as exe:
#             return Response({"detail": "Error creating user", "error": str(exe)}, status=status.HTTP_400_BAD_REQUEST)
