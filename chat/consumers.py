import json

from django.core.checks import messages
from django.contrib.auth import get_user_model

from channels.db import database_sync_to_async

from djangochannelsrestframework.decorators import action

from djangochannelsrestframework.observer import model_observer

from djangochannelsrestframework import permissions
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.consumers import AsyncAPIConsumer

from rest_framework.authtoken.models import Token

from core import models

class FirstConsumer(GenericAsyncAPIConsumer):
    async def accept(self, **kwargs):
        # self.room_name = self.scope['url_route']['kwargs']['room_name']
        # self.user = self.scope['user']

        # Obtain the token in query params
        old_token = str(self.scope['query_string'])
        token = old_token.split("=")[1].replace("'", "")
        print(token)

        # Get the user with that token
        self.user = await self.get_user(token)

        # Get or create a thread
        self.threads = await self.get_or_create_thread(self.user)


        # Accept request
        await super().accept(** kwargs)

        # Join room group
        for i in self.threads:
            await self.channel_layer.group_add(
                f'chat_{i.id}',
                self.channel_name
            )

    @database_sync_to_async
    def get_or_create_thread(self, user):
        thread = []
        try:
            th = models.Thread.objects.filter(users=user)
            for i in th:
                thread.append(i)
        except:
            th = models.Thread.objects.create()
            th.users.add(user)
            thread.append(th)
        print('th:', thread)
        return thread

    @database_sync_to_async
    def get_user(self, token):
        return Token.objects.get(key=token).user


# Receive message from room group
    async def chat_message(self, event):

        message = event['message']
        print('message: ', message)

        # Send message to WebSocket
        await self.send_json(message)


"""---------------><-----------------"""
class ChatConsumer(GenericAsyncAPIConsumer):
    @database_sync_to_async
    def get_msgs(self):
        msgs = []
        ms = models.Message.objects.all()
        for i in ms:
            msgs.append(i.text)
        return msgs

    async def accept(self, **kwargs):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        # self.user = self.scope['user']

        # Obtain the token in query params
        old_token = str(self.scope['query_string'])
        token = old_token.split("=")[1].replace("'", "")
        print(token)

        print('query:', self.scope['url_route']['kwargs']['room_name'])

        # Get the user with that token
        self.user = await self.get_user(token)

        # Get or create a thread
        self.threads = await self.get_or_create_thread(self.user)
        self.current_thread = await self.get_or_create_current_thread()
        print('current_thread:', self.current_thread)

        # Send messages to front

        msgs = await self.get_messages_of_thread()
        print('msgs:', msgs)


        # self.room_name = 'a'
        print('room_name:', self.room_name)
        self.room_group_name = f'chat_{self.room_name}'


        # Accept request
        await super().accept(** kwargs)

        # Join room group
        for i in self.threads:
            await self.channel_layer.group_add(
                f'chat_{i.id}',
                self.channel_name
            )



        # for i in msgs:
        #     await self.channel_layer.group_send(
        #         self.room_group_name,
        #         {
        #             'type': 'chat_message',
        #             'message': i
        #         }
        #     )


        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         'type': 'chat_message',
        #         'message': msgs
        #     }
        # )


        # msgs = await self.get_msgs()
        # await self.send_json(msgs)
        # await self.model_change.subscribe()

# Send messages
        for i in msgs:
            await self.send_json(i)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        text = text_data_json['data']['title']

        # Create a message in database
        msg = await self.create_new_message(text)


# Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                            'type': 'message',
                            'thread': self.room_name,
                            'seen': False,
                            'text': msg.text,
                            'hour': str(msg.created),
                            'owner': msg.owner.username,
                            'is_mine': bool(msg.owner != self.user),
                            'owner_avatar': str(msg.owner.avatar)
                            }
            }
        )
        print('receive_sended')

    @database_sync_to_async
    def get_messages_of_thread(self):
        # get the messages of a thread
        msgs = []
        sub_msg = []
        # for l in self.threads:
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
        #         'thread': l.id,
        #         'data': sub_msg
        #     })
        #     sub_msg = []
        for i in self.current_thread.messages.all():
            # msgs.append(i.text)
            msgs.append({
                'seen': False,
                'text': i.text,
                'hour': str(i.created),
                'owner': i.owner.username,
                'thread': self.current_thread.id,
                'is_mine': i.owner == self.user,
                'owner_avatar': str(i.owner.avatar)
            })
        print('MENSAGES:', msgs)
        return msgs

    # @database_sync_to_async
    # def get_messages_of_thread(self):
    #     # get the messages of a thread
    #     msgs = []
    #     for l in self.threads:
    #         for i in l.messages.all():
    #             # msgs.append(i.text)
    #             msgs.append({
    #                 'seen': False,
    #                 'text': i.text,
    #                 'owner': i.owner.username,
    #                 'thread': l.id
    #             })
    #     return msgs

    @database_sync_to_async
    def create_new_message(self, text):
        """Create a new message in database"""
        msg = models.Message.objects.create(text=text, owner=self.user)
        th = models.Thread.objects.get(id=self.room_name)
        th.messages.add(msg)
        return msg

    @database_sync_to_async
    def get_or_create_thread(self, user):
        thread = []
        try:
            th = models.Thread.objects.filter(users=user)
            for i in th:
                thread.append(i)
        except:
            th = models.Thread.objects.create()
            th.users.add(user)
            thread.append(th)
        print('th:', thread)
        return thread

    @database_sync_to_async
    def get_or_create_current_thread(self):
        thread = None
        try:
            thread = models.Thread.objects.get(id=self.room_name)
        except:
            thread = models.Thread.objects.create()
        print('current_th:', thread)
        return thread

    @database_sync_to_async
    def get_user(self, token):
        return Token.objects.get(key=token).user


# Receive message from room group
    async def chat_message(self, event):

        message = event['message']
        print('message: ', message)

        # Send message to WebSocket
        await self.send_json(message)
