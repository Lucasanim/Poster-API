def home(self, room_name):
    return {'room_name': room_name}

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth import get_user_model

from core.models import Thread, Message

class ReturnThreads(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, format=None):

        threads = Thread.objects.filter(users=request.user)
        ths = []
        users = []
        avatar = ''
        for i in threads:
            for l in i.users.all():
                users.append(l.username)
                if len(i.users.all()) < 3 and l.id != request.user.id:
                    avatar = str(l.avatar)
            ths.append({
                'id': i.id,
                'users': users,
                'avatar': avatar
            })
            users=[]
        return Response(ths)


class CreateThreadAPIView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, format=None):
        other_user = get_user_model().objects.get(id=request.data.get('id'))
        print('OT:', other_user)
        thread = Thread.objects.create()
        thread.users.add(other_user)
        thread.users.add(request.user)
        return Response({'id': thread.id})
