from rest_framework import serializers

from users.models import Payment, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "phone_number", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["amount", "paid_post", "user", "stripe_payment_id", "link_payment"]
        extra_kwargs = {
            "user": {"read_only": True},  # Сделал поле read-only
        }
