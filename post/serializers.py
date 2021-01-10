from rest_framework import serializers

from core.models import Post


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post objects"""

    class Meta:
        model = Post
        fields = ('id', 'title', 'description', 'user')
        read_only_fields = ('id', 'user')