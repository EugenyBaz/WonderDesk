from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =  ["id", "phone_number", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}