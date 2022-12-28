from rest_framework import serializers

from users.models import CustomUser
from recipes.models import Subscribe
from foodgram.settings import MAX_LENGTH


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_authenticated:
            return Subscribe.objects.filter(
                user=self.context['request'].user, author=obj
            ).exists()
        return False


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        max_length=MAX_LENGTH,
        required=True,
    )
    current_password = serializers.CharField(
        max_length=MAX_LENGTH,
        required=True,
    )

    class Meta:
        model = CustomUser
