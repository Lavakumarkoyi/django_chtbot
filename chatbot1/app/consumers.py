from django.contrib.auth.models import User
from channels.consumer import AsyncConsumer
from django.contrib.auth import get_user_model
import asyncio
import json
from django.shortcuts import render
from datetime import datetime
from channels.auth import login
from asgiref.sync import async_to_sync
from sadmin.models import *
from django.contrib.auth.models import User
import random
from channels.exceptions import StopConsumer
from channels.db import database_sync_to_async

import pymongo
from bson.objectid import ObjectId
client = pymongo.MongoClient("localhost", 27017)

db = client.chatbot

print(db)


class ChatConsumer(AsyncConsumer):

    # print(User.objects.all())

    questions = []
    welcome = 'hi welcome to my chatbot'
    goodbye = 'Thank you for providing your information'
    i = 0

    MessageData = []

    j = 0

    group_ids = ''

    intent_ids = []

    groups = []

    @database_sync_to_async
    def get_client_id(self):
        user = self.scope['user']
        user_id = user.id
        client_id = client_user.objects.get(
            user_id_id=user_id).client_id_id

        print("client_id", client_id)

        return client_id

    async def websocket_connect(self, event):
        self.questions = []
        user = self.scope['user']
        bot_id = self.scope['url_route']['kwargs']['bot_id']
        username = self.scope['url_route']['kwargs']['username']

        #user = User.objects.get(username=username)

        user_id = user.id

        client_id = await self.get_client_id()

        print(client_id, user_id)

        bot_collection = 'client{}_bots'.format(client_id)

        public_group = 'client{}_public_groups'.format(client_id)
        private_group = 'client{}_private_groups'.format(client_id)

        public_intent = 'client{}_public_intents'.format(client_id)
        private_intent = 'client{}_private_intents'.format(client_id)

        bot = db[bot_collection].find_one({'_id': ObjectId(bot_id)})
        self.welcome = bot['bot_welcome_message']
        self.goodbye = bot['bot_goodbye_message']

        self.group_ids = bot['group_ids']

        print("group ids", self.group_ids)

        for group_id in self.group_ids:
            print(group_id, type(group_id))
            public_groups = db[public_group].find_one(
                {'_id': ObjectId(group_id)})
            print("public group", public_group)
            if public_groups is not None:
                for intent in public_groups['intent_ids']:
                    self.intent_ids.append(intent)
                print('intent_ids', self.intent_ids)
            private_groups = db[private_group].find_one(
                {'_id': ObjectId(group_id)})
            if private_groups is not None:
                for intent in private_groups['intent_ids']:
                    self.intent_ids.append(intent)

        for intent in self.intent_ids:
            intent1 = db[public_intent].find_one({'_id': ObjectId(intent)})
            if intent1 is not None:
                question = {
                    'response_type': intent1['response_type'],
                    'responses': intent1['intent_response']
                }
                self.questions.append(question)

            intent2 = db[private_intent].find_one({'_id': ObjectId(intent)})
            if intent2 is not None:
                question = {
                    'response_type': intent2['response_type'],
                    'responses': intent2['intent_response']
                }
                self.questions.append(question)

        for group in self.group_ids:
            group1 = db[public_group].find_one({'_id': ObjectId(group)})
            if group1 is not None:
                self.groups.append(group1)

            group2 = db[private_group].find_one({'_id': ObjectId(group)})
            if group2 is not None:
                self.groups.append(group2)

        print("Bot intents", self.intent_ids, end="")
        print("Bot groups", self.group_ids, end="")

        await self.send({
            'type': 'websocket.accept',
        })

        msg = {
            'msg': self.welcome,
            'type': "welcome"
        }

        await self.send({
            'type': 'websocket.send',
            'text': json.dumps(msg)
        })

    async def websocket_receive(self, event):

        print(event)

        print(event.get('text'))
        user = self.scope['user']

        if user.is_authenticated:
            username = user.username

        if event.get('text') == 'opened':
            if len(self.questions) > 0:
                print(self.questions[self.i])
                msg = {
                    'msg': self.questions[self.i],
                    'type': 'normal'
                }
                await self.send({
                    'type': 'websocket.send',
                    'text': json.dumps(msg)
                })

                self.i = self.i + 1

                print(self.i)

                print(len(self.questions))

                for k in self.questions:
                    print(k, end="")
            else:
                msg = {
                    'msg': self.goodbye,
                    'type': 'goodbye'
                }

                await self.send({
                    'type': 'websocket.send',
                    'text': json.dumps(msg)
                })

                self.scope['session'].save()

        else:
            if self.questions[self.i - 1]['response_type'] == 'multichoice':
                option = event.get('text', None)

                multichoice = self.questions[self.i-1]['responses']

                for i in range(1, len(multichoice)):
                    if multichoice[i]['option'] == option:
                        print('Multitple choice option is matched')
                        if multichoice[i]['redirection'] == "3":
                            # redirect to intent
                            intent_id = multichoice[i]['action']
                            count = 0
                            for intent in self.intent_ids:
                                count = count + 1
                                if intent == intent_id:
                                    self.i = count - 1
                        if multichoice[i]['redirection'] == '5':
                            # Bot termination
                            count = 0
                            for intent in self.intent_ids:
                                count = count + 1
                            self.i = count
                        if multichoice[i]['redirection'] == '6':
                            # reply with text
                            print("Entered to rpy with text")
                            rpy = {
                                'response_type': 'text',
                                'responses': [multichoice[i]['action']]
                            }
                            print(rpy)

                            msg = {
                                'msg': rpy,
                                'type': 'normal',
                            }
                            await self.send({
                                'type': 'websocket.send',
                                'text': json.dumps(msg)
                            })

                            if self.i < len(self.questions):

                                msg = {
                                    'msg': self.questions[self.i],
                                    'type': 'normal'
                                }

                                await self.send({
                                    'type': 'websocket.send',
                                    'text': json.dumps(msg)
                                })
                            else:

                                self.i = self.i + 1

                # print(self.questions[self.i])
                if multichoice[i]['redirection'] == '7':
                    # redirect to group
                    group_id = multichoice[i]['action']
                    # first getting the goupid we want to redirect
                    count = 0
                    for group in self.group_ids:
                        # after searching the group_id in groups_id
                        count = count + 1
                        if group == group_id:
                            # if the group_id is present in group_ids
                            for g in self.groups:
                                # Then go to the groups to find the intents in a group
                                # search that the group_id matched with actual group_id ['_id']
                                if g['_id'] == group_id:
                                    # if that matches get the intents from the group
                                    inten = g['intent_ids']
                                    count1 = 0
                                    for inte in intent_id:
                                        # then take the first intent_id from the groups and match that intent in intent_ids and make a count to the start the intent with
                                        count1 = count1 + 1
                                        if inte == inten[0]:
                                            self.i = count1-1

            if self.i < len(self.questions):
                print("Entered into text response")
                msg = {
                    'msg': self.questions[self.i],
                    'type': 'normal'
                }
                await self.send({
                    'type': 'websocket.send',
                    'text': json.dumps(msg)
                })

                self.i = self.i + 1

            else:
                msg = {
                    'msg': self.goodbye,
                    'type': 'goodbye'
                }
                await self.send({
                    'type': 'websocket.send',
                    'text': json.dumps(msg)
                })

                # self.scope["session"].save()

    async def websocket_disconnect(self, event):
        print(event)
        raise StopConsumer()
