from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user import views

app_name = 'user'

router = DefaultRouter()
router.register('owner', views.PostOwnerViewSet)
router.register('search', views.SearchUsersViewSet)

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name="create"),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('', include(router.urls)),

    path('follow/<pk>/', views.FollowAPIView.as_view(), name='follow'),
    path('unfollow/<pk>/', views.UnfollowAPIView.as_view(), name='unfollow'),
]