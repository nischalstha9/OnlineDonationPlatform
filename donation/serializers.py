from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from .models import Donation, Category

class CategorySerializer(ModelSerializer):
    parent_name = SerializerMethodField()
    class Meta:
        model = Category
        fields = "__all__"

    def get_parent_name(self, obj):
        try:
            return obj.parent.name
        except:
            return None

class DonationSerializer(ModelSerializer):
    category_name = SerializerMethodField()
    doner_name = SerializerMethodField()
    class Meta:
        model = Donation
        fields = "__all__"
        extra_kwargs = {
            "user":{
                "required":False
            }
        }

    def get_category_name(self, obj):
        return obj.category.name

    def get_doner_name(self, obj):
        user = obj.user
        return f"{user.first_name} {user.last_name}"

    def validate(self, attrs):
        attrs['doner'] = self.context.get('view').request.user
        return super().validate(attrs)