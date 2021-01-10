from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.core import serializers

from core.models import Post, Follows

from post.serializers import PostSerializer


class PostViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin):
    """viewset for user owned posts"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(post__isnull=False)

        following = Follows.objects.get(user=self.request.user)
        fws = []
        for i in following.follows.all():
            fws.append(i.first_name)

        queryset = queryset.filter(user__first_name__in=fws).order_by('-id')

        # queryset = queryset.filter(
        #     user=self.request.user
        # ).order_by('-title').distinct()

        return queryset

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)

    # def perform_update(self, serializer):
    #     serializer.save()


class MyPostViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin):
    """List the users post"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        queryset = queryset.filter(user=self.request.user).order_by('-id').distinct()

        return queryset

    def perform_create(self, serializer):
        """Creates a new post"""
        serializer.save(user=self.request.user)
