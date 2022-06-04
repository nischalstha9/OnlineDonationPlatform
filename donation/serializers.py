from authentication.serializers import CustomUserSerializer
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from .models import Donation, Category, MetaImage

class CategorySerializer(ModelSerializer):
    parent_name = SerializerMethodField()
    num_donations = SerializerMethodField()
    class Meta:
        model = Category
        fields = "__all__"

    def get_parent_name(self, obj):
        try:
            return obj.parent.name
        except:
            return None

    def get_num_donations(self, obj):
        try:
            return obj.num_donations
        except:
            return None

class DonationSerializer(ModelSerializer):
    category_name = SerializerMethodField()
    doner = SerializerMethodField()
    class Meta:
        model = Donation
        fields = "__all__"
        extra_kwargs = {
            "user":{
                "required":False
            },
            "likes":{
                "required":False
            }
        }

    def get_category_name(self, obj):
        return obj.category.name

    def get_doner(self, obj):
        user = obj.user
        return CustomUserSerializer(user).data

    def validate(self, attrs):
        attrs['user'] = self.context.get('view').request.user
        return super().validate(attrs)



class MetaImageListCreateSerializer(ModelSerializer):
    class Meta:
        model = MetaImage
        fields = "__all__"
        