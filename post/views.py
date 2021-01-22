from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

from django.core import serializers

from core.models import Post, Follows

from post.serializers import PostSerializer, PostImageSerializer


class PostViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin):
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

        return queryset

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class MyPostViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.DestroyModelMixin):
    """List the users post"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    # parser_classes = (JSONParser, MultiPartParser, FormParser,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(post__isnull=False)
        queryset = queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

        return queryset

    def perform_create(self, serializer):
        """Creates a new post"""
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        """Return apropiate serializer class"""
        if self.action == 'retrieve':
            return PostSerializer
        elif self.action == 'upload_image':
            return PostImageSerializer
        return self.serializer_class
    
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """upload an image to a post"""
        post = self.get_object()
        print('request:', request)
        print('request.data:', request.data)
        serializer = self.get_serializer(
            post,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UsersPostsViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin):
    """Return posts of a user"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def get_queryset(self):
        """Return the correct posts of the user"""
        queryset = self.queryset

        id = self.request.query_params.get('id')
        print('id', id)
        if id:
            queryset = queryset.filter(user = id)
        return queryset
