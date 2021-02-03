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
        # msgs = []
        # sub_msg = []
        # for l in threads:
        #     for i in l.messages.all():
        #         # msgs.append(i.text)
        #         sub_msg.append({
        #             'seen': False,
        #             'text': i.text,
        #             'owner': i.owner.username,
        #             'thread': l.id
        #         })
        #     msgs.append({
        #         'type': 'thread',
        #         'id': l.id,
        #         'data': sub_msg
        #     })
        #     sub_msg = []
        # print('MENSAGES:', msgs)
        # return Response(msgs)
        ths = []
        for i in threads:
            ths.append(i.id)
        return Response(ths)

class ReturnUser(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, format=None):
        user = get_user_model().objects.get(id=request.user.id)
        print('user:', user)

        response = {
            'id': user.id,
            'username': user.username
        }

        return Response(response)
