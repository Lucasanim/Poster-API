from django.urls import path, include
from rest_framework.routers import DefaultRouter

from post import views

router = DefaultRouter()
router.register('posts', views.PostViewSet)
router.register('my-posts', views.MyPostViewSet)
router.register('users-posts', views.UsersPostsViewSet)

app_name = 'post'

urlpatterns = [
    path('', include(router.urls))
]