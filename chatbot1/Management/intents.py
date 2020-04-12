from django import template
from django.shortcuts import render, redirect
from django.views.generic import View
from sadmin.views import navbar
from django.http import HttpResponseRedirect, HttpResponse
from sadmin.models import *
from datetime import datetime
from rest_framework.views import APIView
from sadmin.models import *
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

import pymongo
import os
from bson.objectid import ObjectId
client = pymongo.MongoClient("localhost", 27017)

db = client.chatbot


# Create your views here.


class create_intent_form(View):
    def get(self, request):

        totalMenu = navbar(request.user)
        return render(request, 'bots/create-intent-form.html', {'Menudata': totalMenu, 'username': request.user.username})

    def post(self, request):

        user_id = request.user.id
        totalMenu = navbar(request.user)

        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        intent_name = request.POST['IntentName']
        intent_description = request.POST['IntentDescription']
        # checking whether the intent with that name already exists in the db

        if intent_name == '':
            return render(request, 'bots/create-intent-form.html', {'Menudata': totalMenu, 'username': request.user.username, 'message': 'Intent Name should not be Empty'})

        if intent_description == '':
            return render(request, 'bots/create-intent-form.html', {'Menudata': totalMenu, 'username': request.user.username, 'message': 'Intent Description should not be Empty'})

        # check it in both private and public collections
        public_collection = 'client{}_public_intents'.format(client_id)
        private_collection = 'client{}_private_intents'.format(client_id)
        intent_find1 = db[public_collection].find_one(
            {'intent_name': intent_name, "user_id": user_id})
        intent_find2 = db[private_collection].find_one(
            {'intent_name': intent_name, "user_id": user_id})

        # check wether the intent present if it presents

        if intent_find1 is not None or intent_find2 is not None:
            return render(request, 'bots/create-intent-form.html', {'Menudata': totalMenu, 'username': request.user.username, 'message': 'Intent already exists'})

        privacy = request.POST['privacy']

        phrases = []

        for key in request.POST.keys():
            if 'Phrase' in key:
                phrases.append(request.POST[key])

        collection = 'client{}_{}_intents'.format(
            client_id, privacy)

        keys = request.POST.keys()

        db[collection].insert_one({'intent_name': intent_name, 'intent_description': intent_description, 'intent_phrases': phrases, 'created_on': datetime.now(
        ), 'created_by': request.user.username, 'user_id': user_id, 'client_id': client_id, 'intent_response': []})

        fetch_intent_id = db[collection].find_one(
            {'intent_name': intent_name, 'user_id': user_id})

        intent_id = fetch_intent_id['_id']
        url = '/intents/response-form/%s' % intent_id

        return HttpResponseRedirect(url)


class create_intent(View):
    def get(self, request):
        user_id = request.user.id
        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        public_collection = 'client{}_public_intents'.format(client_id)
        private_collection = 'client{}_private_intents'.format(client_id)

        db[public_collection].remove(
            {'response_type': {'$exists': False}})
        db[private_collection].remove(
            {'response_type': {'$exists': False}})

        user_public_intents = db[public_collection].find()

        u_public_i = []
        for intent in user_public_intents:
            intent['id'] = intent['_id']
            u_public_i.append(intent)

        user_private_intents = db[private_collection].find(
            {'user_id': user_id})

        u_private_i = []
        for intent in user_private_intents:
            intent['id'] = intent['_id']
            u_private_i.append(intent)

        u_private_i.reverse()
        u_public_i.reverse()

        totalMenu = navbar(request.user)
        return render(request, 'bots/intents.html', {'Menudata': totalMenu, 'username': request.user.username, 'public_intents': u_public_i, 'private_intents': u_private_i})


class IntentResponseView(View):
    def get(self, request, intent_id):

        user_id = request.user.id
        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        public_collection = 'client{}_public_intents'.format(client_id)
        private_collection = 'client{}_private_intents'.format(client_id)
        find_intent1 = db[public_collection].find_one(
            {'_id': ObjectId(intent_id)})
        find_intent2 = db[private_collection].find_one(
            {'_id': ObjectId(intent_id)})

        public_groups = 'client{}_public_groups'.format(client_id)
        private_groups = 'client{}_private_groups'.format(client_id)

        public_total_groups = db[public_groups].find()
        private_total_groups = db[private_groups].find({'user_id': user_id})

        total_groups = []

        for group in public_total_groups:
            total_groups.append(group)

        for group in private_total_groups:
            total_groups.append(group)

        public_total_intents = db[public_collection].find()
        private_total_intents = db[private_collection].find(
            {'user_id': user_id})

        total_intents = []

        for intent in private_total_intents:
            intent['id'] = intent['_id']
            total_intents.append(intent)

        for intent in public_total_intents:
            intent['id'] = intent['_id']
            total_intents.append(intent)

        if find_intent1 is not None or find_intent2 is not None:
            totalMenu = navbar(request.user)
            return render(request, 'bots/response-form.html', {'Menudata': totalMenu, 'username': request.user.username, 'intents': total_intents, 'groups': total_groups})

    def post(self, request, intent_id):

        user_id = request.user.id
        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        response_type = request.POST['IntentresponseType']

        public_collection = 'client{}_public_intents'.format(client_id)
        private_collection = 'client{}_private_intents'.format(client_id)

        check_intent_id1 = db[public_collection].find_one(
            {'_id': ObjectId(intent_id)})
        check_intent_id2 = db[private_collection].find_one(
            {'_id': ObjectId(intent_id)})

        responses = []

        if response_type == 'text':
            for key in request.POST.keys():
                if 'Response' in key:
                    responses.append(request.POST[key])

        if response_type == "multichoice":
            print("total Multiple choice data", request.POST)
            #print("Multiple choice data", request.POST['option'])
            for key in request.POST.keys():
                if 'redirection' in key:
                    print("entered into redirection change")
                    if request.POST[key] == '1':
                        print('No action')
                        request.POST[key] == 'NoAction'
                    elif request.POST[key] == '2':
                        request.POST[key] == 'redirectUrl'
                    elif request.POST[key] == '3':
                        request.POST[key] == 'redirectIntent'
                    elif request.POST[key] == '4':
                        request.POST[key] == 'flowIdentifier'
                    elif request.POST[key] == '5':
                        request.POST[key] == 'botTermination'
                    elif request.POST[key] == '6':
                        request.POST[key] == 'replyText'
                    elif request.POST[key] == '7':
                        request.POST[key] == 'redirectGroup'

            options = []
            values = []
            redirections = []
            actions = []

            responsetexts = {
                'responseText': request.POST['responsetext'],
                'alternateresponseText': request.POST['alternateresponsetext']
            }

            responses.append(responsetexts)

            for key in request.POST.keys():
                if 'option' in key:
                    options.append(request.POST[key])
                if 'value' in key:
                    values.append(request.POST[key])
                if 'redirection' in key:
                    redirections.append(request.POST[key])
                if 'action' in key:
                    actions.append(request.POST[key])

            count = 0

            print("total values seperately", options,
                  values, redirections, actions)

            for (option, value, redirection, action) in zip(options, values, redirections, actions):
                choices = {}
                choices['option'] = option
                choices['value'] = value
                choices['redirection'] = redirection
                choices['action'] = action
                responses.append(choices)

                print(responses)

                count = count + 1

            print("{count}", choices)

        if response_type == 'mutipleSelection':
            response_text = request.POST['responsetext']
            options = []
            for key in request.POST.keys():
                if 'option' in key:
                    options.append(request.POST[key])

            mutlichoice = {
                'response_text': response_text,
                'options': options
            }

            responses.append(mutlichoice)

        if response_type == 'attachment':
            print(request.FILES)
            print(request.POST['imgtype'])
            attachmenttitles = []
            images = []
            for key in request.POST.keys():
                if 'attachmenttitle' in key:
                    attachmenttitles.append(request.POST[key])
            if request.POST['imgtype'] == 'filesys':
                print(request.FILES)
                for key in request.FILES.keys():
                    print(request.FILES[key])
                    image_path = default_storage.save(os.path.join(
                        'media', 'attachment'), ContentFile(request.FILES[key].read()))
                    print(request.FILES[key])
                    images.append(image_path)

            if request.POST['imgtype'] == 'imageurl':
                for key in request.POST.keys():
                    if 'image' in key:
                        images.append(request.POST[key])

            for (title, image) in zip(attachmenttitles, images):
                attachment = {}
                attachment['title'] = title
                attachment['image'] = image

                responses.append(attachment)

        print(intent_id)

        if check_intent_id1 is not None:
            db[public_collection].update_one(
                {'_id': ObjectId(intent_id)}, {"$set": {"intent_response": responses, 'response_type': response_type}})

            print('updated successfully in public intents')

            return redirect('/bot-console/intents/')
        else:
            db[private_collection].update_one(
                {'_id': ObjectId(intent_id)}, {"$set": {"intent_response": responses, 'response_type': response_type}})

            print('updated successfully in private intents')

            # return HttpResponse("Hi your data is successfully updated")

            return redirect('/bot-console/intents/')


class delete_intent(View):
    def get(self, request, intent_id):

        user_id = request.user.id
        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        public_collection = 'client{}_public_intents'.format(client_id)
        private_collection = 'client{}_private_intents'.format(client_id)

        public_groups_collection = 'client{}_public_groups'.format(client_id)
        private_groups_collection = 'client{}_private_groups'.format(client_id)

        one = db[public_groups_collection].update_many(
            {}, {'$pull': {"intent_ids": intent_id}}, True)
        two = db[private_groups_collection].update_many(
            {}, {'$pull': {'intent_ids': intent_id}}, True)

        three = db[public_groups_collection].update_many(
            {}, {'$pull': {'intents': {'intent_id': intent_id}}}, True)
        four = db[private_groups_collection].update_many(
            {}, {'$pull': {'intents': {'intent_id': intent_id}}}, True)

        one = db[public_collection].find_one({'_id': ObjectId(intent_id)})
        two = db[private_collection].find_one({'_id': ObjectId(intent_id)})

        if one is not None:
            if one.response_type == 'attachment':
                images = one.intent_response[0].image

                for image in images:
                    os.remove(os.path.join(settings.BASE_DIR, image))
                    print(os.path.join(settings.BASE_DIR, image))
            db[public_collection].remove({'_id': ObjectId(intent_id)})

            return redirect('/bot-console/intents/')

        if two is not None:
            print("deleting intent", two['response_type'])
            if two['response_type'] == 'attachment':
                for response in two['intent_response']:
                    image = response['image']

                    path = os.path.join(settings.BASE_DIR,
                                        'chatbot1', 'media', image).split('\\')
                    last_Element = path[len(path)-1]
                    final_element = last_Element.split('/')
                    total_element = []
                    path[len(path) - 1] = final_element[0]

                    path.append(final_element[1])

                    s = '//'

                    print(s.join(path))

                    os.remove(s.join(path))
                    print(os.path.join(settings.BASE_DIR, image))

            db[private_collection].remove({'_id': ObjectId(intent_id)})

            return redirect('/bot-console/intents/')

        return HttpResponse('No intent found')


# editing intents view

class Edit_intent(View):
    def post(self, request):
        totalMenu = navbar(request.user)
        user_id = request.user.id
        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        private_collection = 'client{}_private_intents'.format(client_id)
        public_collection = 'client{}_public_intents'.format(client_id)

        edited = request.POST['edited']
        if edited == 'false':

            intent_id = request.POST['intent_id']

            i_private_find = db[private_collection].find_one(
                {'_id': ObjectId(intent_id), 'user_id': user_id, 'client_id': client_id})

            i_public_find = db[public_collection].find_one(
                {'_id': ObjectId(intent_id), 'user_id': user_id, 'client_id': client_id})

            print(i_private_find)

            if i_private_find is not None:

                i_private_find['id'] = i_private_find['_id']

                # for intent in i_private_find:
                #     intent['id'] = intent['_id']
                #     u_private_i.append(intent)

                return render(request, 'edit/create-intent-form.html', {'Menudata': totalMenu, 'username': request.user.username, 'intent':  i_private_find})
            else:
                i_public_find['id'] = i_public_find['_id']
                # for intent in i_public_find:
                #     intent['id'] = intent['_id']
                #     u_public_i.append(intent)

                return render(request, 'edit/create-intent-form.html', {'Menudata': totalMenu, 'username': request.user.username, 'intent': i_public_find})

            return render(request, 'edit/create-intent-form.html', {'Menudata': totalMenu, 'username': request.user.username})

        if edited == 'true':
            intent_id = request.POST['intent_id']
            privacy = request.POST['privacy']

            intent_name = request.POST['IntentName']
            intent_description = request.POST['IntentDescription']

            print(intent_name)

            phrases = []

            for key in request.POST.keys():
                if 'Phrase' in key:
                    phrases.append(request.POST[key])

            if privacy == 'private':
                intent_find_private = db[private_collection].find_one(
                    {'_id': ObjectId(intent_id)})

                if intent_find_private is not None:
                    db[private_collection].update_one({'_id': ObjectId(intent_id)}, {'$set': {
                        'intent_name': intent_name, 'intent_description': intent_description, 'intent_phrases': phrases}}, upsert=True)

                    print('updated successfully in private intents')

                    url = '/edit/edit_response/%s' % intent_id

                    return HttpResponseRedirect(url)

                if intent_find_private is None:
                    public_intent = db[public_collection].find_one(
                        {'_id': ObjectId(intent_id)})

                    db[private_collection].insert_one({'intent_name': intent_name, 'intent_description': intent_description, 'intent_phrases': phrases, 'created_on': datetime.now(
                    ), 'created_by': request.user.username, 'user_id': user_id, 'client_id': client_id, 'intent_response': public_intent['intent_response'], 'response_type': public_intent['response_type']})

                    db[public_collection].remove({'_id': ObjectId(intent_id)})

                    fetch_intent_id = db[private_collection].find_one(
                        {'intent_name': intent_name, 'user_id': user_id})

                    new_intent_id = fetch_intent_id['_id']
                    url = '/edit/edit_response/%s' % new_intent_id

                    return HttpResponseRedirect(url)

            if privacy == 'public':
                intent_find_public = db[public_collection].find(
                    {'_id': intent_id})

                if intent_find_public is not None:
                    db[public_collection].update_one({'_id': ObjectId(intent_id)}, {'$set': {
                        'intent_name': intent_name, 'intent_description': intent_description, 'intent_phrases': phrases}})

                    url = '/edit/edit_response/%s' % intent_id

                    return HttpResponseRedirect(url)

                if intent_find_public is None:
                    db[public_collection].insert_one({'intent_name': intent_name, 'intent_description': intent_description, 'intent_phrases': phrases, 'created_on': datetime.now(
                    ), 'created_by': request.user.username, 'user_id': user_id, 'client_id': client_id, 'intent_response': []})

                    db[private_collection].remove({'_id': ObjectId(intent_id)})

                    fetch_intent_id = db[public_collection].find_one(
                        {'intent_name': intent_name, 'user_id': user_id})

                    new_intent_id = fetch_intent_id['_id']
                    url = '/edit/edit_response/%s' % new_intent_id

                    return HttpResponseRedirect(url)


class Edit_response(View):
    def get(self, request, intent_id):
        totalMenu = navbar(request.user)
        user_id = request.user.id

        client_id = client_user.objects.get(user_id_id=user_id).client_id_id

        public_collection = 'client{}_public_intents'.format(client_id)
        private_collection = 'client{}_private_intents'.format(client_id)

        intent_in_public_collection = db[public_collection].find_one(
            {'_id': ObjectId(intent_id)})
        intent_in_private_collection = db[private_collection].find_one(
            {'_id': ObjectId(intent_id)})

        if intent_in_public_collection is not None:
            response_type = intent_in_public_collection['response_type']
            intent_responses = intent_in_public_collection['intent_response']

            return render(request, 'edit/response-form.html', {'response_type': response_type, 'intent_responses': intent_responses,  'Menudata': totalMenu, 'username': request.user.username})

            print(response_type)

        if intent_in_private_collection is not None:
            response_type = intent_in_private_collection['response_type']
            intent_responses = intent_in_private_collection['intent_response']

            print(response_type)

            return render(request, 'edit/response-form.html', {'response_type': response_type, 'intent_responses': intent_responses, 'Menudata': totalMenu, 'username': request.user.username})

    def post(self, request, intent_id):
        responses = []

        response_type = request.POST['IntentresponseType']
        for key in request.POST.keys():
            if 'Response' in key:
                responses.append(request.POST[key])
        user_id = request.user.id
        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        print("intent responses", responses)
        print("intent_response_type", response_type)
        print('clinet_id', client_id)

        public_collection = 'client{}_public_intents'.format(client_id)
        private_collection = 'client{}_private_intents'.format(client_id)

        print(public_collection, private_collection)
        check_intent_id1 = db[public_collection].find_one(
            {'_id': ObjectId(intent_id)})
        check_intent_id2 = db[private_collection].find_one(
            {'_id': ObjectId(intent_id)})

        print(intent_id)

        if check_intent_id1 is not None:
            db[public_collection].update_one(
                {'_id': ObjectId(intent_id)}, {"$set": {"intent_response": responses, 'response_type': response_type}})

            print('updated successfully in public intents')

            return redirect('/bot-console/intents/')
        else:
            db[private_collection].update_one(
                {'_id': ObjectId(intent_id)}, {"$set": {"intent_response": responses, 'response_type': response_type}})

            print('updated successfully in private intents')

            # return HttpResponse("Hi your data is successfully updated")

            return redirect('/bot-console/intents/')


class intent_images(View):
    def get(self, request):
        user_id = request.user.id

        client_id = client_user.objects.get(user_id_id=user_id).client_id_id

        public_collection = 'client{}_public_intents'.format(client_id)
        private_collection = 'client{}_private_intents'.format(client_id)

        intents = db[private_collection].find({'user_id': user_id})

        for intent in intents:
            if intent['response_type'] == 'attachment':
                urls = intent['intent_response'][0]['images']

                return render(request, 'superadmin/intent_images.html', {'urls': urls})
