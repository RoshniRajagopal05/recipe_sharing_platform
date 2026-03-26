from rest_framework import serializers
from .models import Recipe,User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class RecipeSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    image_upload = serializers.SerializerMethodField()
    class Meta:
        model = Recipe
        fields = '__all__'
    def get_image_upload(self, obj):
        if obj.image_upload:
            return obj.image_upload.url
        return None

