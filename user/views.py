from rest_framework import generics, authentication, permissions, mixins, viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken, APIView
from rest_framework.settings import api_settings
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from django.db.models import Q

from user.serializers import AuthTokenSerializer, UserSerializer
from core.models import Follows, Followers


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for a user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authentication user"""
        return self.request.user


class PostOwnerViewSet(viewsets.GenericViewSet,
                       mixins.ListModelMixin):
    """Return the owner of a post"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        """Return the correct queryset"""

        queryset = self.queryset

        # id = self.request.query_params.get('id')

        # if id:
        #     queryset = get_user_model().objects.filter(id=id)
        
        follows = Follows.objects.get(user=self.request.user)

        users = []

        queryset = follows.follows.all()

        return queryset


class SearchUsersViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin):
    """Handle search posts"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()

    def get_queryset(self):
        '''Retrieve the search users'''
        queryset = self.queryset

        qs = self.request.query_params.get('qs')

        if qs:
            queryset = queryset.filter(Q(first_name__icontains=qs) | Q(last_name__icontains=qs) | Q(username__icontains=qs))
            # queryset = queryset.filter(Q(first_name__startswith=qs) | Q(last_name__startswith=qs))
        queryset = queryset.exclude(id = self.request.user.id)
        return queryset


class FollowAPIView(APIView):
    """Add a new following to a user"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, pk, format=None):
        user = request.user
        # id = request.query_params.get('id')
        id = request.user.id
        print(id)
        if pk == id:
            return Response({'status':status.HTTP_400_BAD_REQUEST})
        if pk != request.user.id:

            # Add follow to current user

            follow = Follows.objects.get(user=user)
            f_user = get_user_model().objects.get(id=pk)

            if follow and f_user:

                follow.follows.add(f_user)
                follow.save()
                print(follow)

                # Add follower to other user

                follower = Followers.objects.get(user=f_user)
                follower.followers.add(user)
                follower.save()
                print(follower)

                return Response({'status':status.HTTP_200_OK})

            return Response({'status':status.HTTP_400_BAD_REQUEST})
        else:
            return Response({'status':status.HTTP_400_BAD_REQUEST})


class UnfollowAPIView(APIView):
    """Remove a following of user"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, pk, format=None):
        user = request.user

        # Removes the follow of the current user

        follow = Follows.objects.get(user=user)
        f_user = get_user_model().objects.get(id=pk)

        follow.follows.remove(f_user)
        follow.save()

        # Remove follower of the other user

        follower = Followers.objects.get(user=f_user)
        follower.followers.remove(user)
        follower.save()

        return Response({'status':status.HTTP_200_OK})
