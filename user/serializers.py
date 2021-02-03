from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from core.models import Followers, Follows


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""
    # follow = serializers.CharField(source='category.name')

    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name', 'password', 'avatar', 'id', 'his_follows', 'his_followers', 'follow', 'follower', 'username')
        read_only_fields = ('id','his_followers', 'his_follows')
        extra_kwargs = {'password':{'write_only':True, 'min_length': 8}}

    def create(self, validated_data):
        """Create a new user with encrypted password and returns it"""
        user = get_user_model().objects.create_user(**validated_data)
        follower = Followers.objects.create(user=user)
        follows = Follows.objects.create(user=user)
        user.his_followers=follower
        user.his_follows=follows
        user.save()
        return user

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and returns it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type':'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            msg = _('Unable to authenticate the user with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')
        attrs['user'] = user
        return attrs


class UserImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to user"""

    class Meta:
        model = get_user_model()
        fields = ('id', 'avatar')
        read_only_fields = ('id',)
