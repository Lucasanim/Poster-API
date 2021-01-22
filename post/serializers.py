from rest_framework import serializers

from core.models import Post


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post objects"""

    class Meta:
        model = Post
        fields = ('id', 'title', 'description', 'user', 'image')
        read_only_fields = ('id', 'user')


class PostImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading image for posts"""

    class Meta:
        model = Post
        fields = ('id', 'image')
        read_only_fields = ('id',)
