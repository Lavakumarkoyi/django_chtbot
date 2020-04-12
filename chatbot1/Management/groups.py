from django.shortcuts import render, redirect
from django.views.generic import View
from sadmin.views import navbar
from datetime import datetime
from django.http import HttpResponseRedirect
from sadmin.models import *
from sadmin.models import *

import pymongo
from bson.objectid import ObjectId
client = pymongo.MongoClient("localhost", 27017)

db = client.chatbot


# Create your views here.


class create_group(View):
    def get(self, request):
        totalMenu = navbar(request.user)
        user_id = request.user.id

        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        public_collection = 'client{}_public_groups'.format(client_id)
        private_collection = 'client{}_private_groups'.format(client_id)

        db[public_collection].remove(
            {'intent_ids': {'$exists': False}})

        db[private_collection].remove(
            {'intent_ids': {'$exists': False}})

        user_public_groups = db[public_collection].find()

        u_public_g = []
        for intent in user_public_groups:
            intent['id'] = intent['_id']
            u_public_g.append(intent)

        user_private_groups = db[private_collection].find(
            {'user_id': user_id})

        u_private_g = []
        for intent in user_private_groups:
            intent['id'] = intent['_id']
            u_private_g.append(intent)

        u_private_g.reverse()
        u_public_g.reverse()

        # for group in u_public_g:
        #     for intent in group['intents']:
        #         print(intent)

        return render(request, 'bots/create-group.html', {'Menudata': totalMenu, 'username': request.user.username, 'public_groups': u_public_g, 'private_groups': u_private_g})


class create_group_form(View):
    def get(self, request):
        totalMenu = navbar(request.user)
        return render(request, 'bots/create-group-form.html', {'Menudata': totalMenu, 'username': request.user.username})

    def post(self, request):
        totalMenu = navbar(request.user)
        group_data = request.POST
        group_name = request.POST['GroupName']
        group_description = request.POST['GroupDescription']
        group_privacy = request.POST['privacy']

        if group_name == '':
            return render(request, 'bots/create-group-form.html', {'Menudata': totalMenu, 'username': request.user.username, 'message': 'Group Name Should Not Be Empty'})

        if group_description == '':
            return render(request, 'bots/create-group-form.html', {'Menudata': totalMenu, 'username': request.user.username, 'message': 'Group Description Should Not Be Empty'})

        user_id = request.user.id

        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        public_collection = 'client{}_public_groups'.format(client_id)
        private_collection = 'client{}_private_groups'.format(client_id)
        group_find1 = db[public_collection].find_one(
            {'group_name': group_name, "user_id": user_id})
        group_find2 = db[private_collection].find_one(
            {'group_name': group_name, "user_id": user_id})

        if group_find1 is not None or group_find2 is not None:
            return render(request, 'bots/create-group-form.html', {'Menudata': totalMenu, 'username': request.user.username, 'message': 'group already exists'})

        collection = 'client{}_{}_groups'.format(
            client_id, group_privacy)

        db[collection].insert_one({'group_name': group_name, "group_description": group_description,
                                   "user_id": user_id, "created_by": request.user.username, "created_on": datetime.now()})

        fetch_group_id = db[collection].find_one(
            {'group_name': group_name, 'user_id': user_id})
        print(fetch_group_id['_id'])
        group_id = fetch_group_id['_id']
        url = '/group-intent/%s' % group_id
        print(url)
        return HttpResponseRedirect(url)


class group_intent(View):
    def get(self, request, group_id):
        print(group_id)

        user_id = request.user.id

        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        public_collection = 'client{}_public_intents'.format(client_id)
        private_collection = 'client{}_private_intents'.format(client_id)

        public_intents = db[public_collection].find()
        private_intents = db[private_collection].find({'user_id': user_id})

        u_public_i = []
        for intent in public_intents:
            intent['id'] = intent['_id']
            u_public_i.append(intent)

        u_private_i = []
        for intent in private_intents:
            intent['id'] = intent['_id']
            u_private_i.append(intent)

        totalMenu = navbar(request.user)
        return render(request, 'bots/group-intent.html', {'Menudata': totalMenu, 'username': request.user.username, "public_intents": u_public_i, "private_intents": u_private_i})

    def post(self, request, group_id):

        # Get request code to display the intents to add them in the group

        user_id = request.user.id

        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        public_collection = 'client{}_public_intents'.format(client_id)
        private_collection = 'client{}_private_intents'.format(client_id)

        public_intents = db[public_collection].find()
        private_intents = db[private_collection].find({'user_id': user_id})

        u_public_i = []
        for intent in public_intents:
            intent['id'] = intent['_id']
            u_public_i.append(intent)

        u_private_i = []
        for intent in private_intents:
            intent['id'] = intent['_id']
            u_private_i.append(intent)

        totalMenu = navbar(request.user)

        #######################################################

        intents = []

        intent_ids = []
        for key in request.POST.keys():
            if 'intent' in key:
                intent_ids.append(request.POST[key])

        if len(intent_ids) <= 0:
            return render(request, 'bots/group-intent.html', {'Menudata': totalMenu, 'username': request.user.username, "public_intents": u_public_i, "private_intents": u_private_i, 'message': 'Please add the intents to the group'})

        intent_names = []

        user_id = request.user.id

        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        public_intents = 'client{}_public_intents'.format(client_id)
        private_intents = 'client{}_private_intents'.format(client_id)

        for intent_id in intent_ids:
            intent_name = db[public_intents].find_one(
                {'_id': ObjectId(intent_id)})
            if intent_name is not None:
                intent_names.append(intent_name['intent_name'])

        for intent_id in intent_ids:
            intent_name = db[private_intents].find_one(
                {'_id': ObjectId(intent_id)})
            if intent_name is not None:
                intent_names.append(intent_name['intent_name'])

        public_collection = 'client{}_public_groups'.format(client_id)
        private_collection = 'client{}_private_groups'.format(client_id)

        for intent_id, intent_name in zip(intent_ids, intent_names):
            intents.append(
                {'intent_id': intent_id, 'intent_name': intent_name})

        check_public_group = db[public_collection].find_one(
            {'_id': ObjectId(group_id)})
        check_private_group = db[private_collection].find_one(
            {'_id': ObjectId(group_id)})

        for intent in intents:
            print('final after sorting', intent)

        if check_public_group is not None:
            db[public_collection].update_one(
                {'_id': ObjectId(group_id)}, {"$set": {"intents": intents, "intent_ids": intent_ids}})

            print('updated successfully in public groups')

            return redirect('/bot-console/groups/')
        else:
            db[private_collection].update_one(
                {'_id': ObjectId(group_id)}, {"$set": {"intents": intents, "intent_ids": intent_ids}})

            print('updated successfully in private groups')

            return redirect('/bot-console/groups/')


class intent_flow(View):
    def post(self, request, group_id):
        print(group_id)
        print(request.POST)
        intent_ids = []
        intent_names = []
        intents = []
        i = 1

        for key in request.POST.keys():
            if i == 1:
                i = i + 1
                continue
            intent_ids.append(request.POST[key])
            i = i + 1

        user_id = request.user.id

        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        public_intents = 'client{}_public_intents'.format(client_id)
        private_intents = 'client{}_private_intents'.format(client_id)

        for intent_id in intent_ids:
            intent_name1 = db[public_intents].find_one(
                {'_id': ObjectId(intent_id)})
            intent_name2 = db[private_intents].find_one(
                {'_id': ObjectId(intent_id)})
            if intent_name1 is not None:
                intent_names.append(intent_name1['intent_name'])
            if intent_name2 is not None:
                intent_names.append(intent_name2['intent_name'])

        public_collection = 'client{}_public_groups'.format(client_id)
        private_collection = 'client{}_private_groups'.format(client_id)

        for intent_id, intent_name in zip(intent_ids, intent_names):
            intents.append(
                {'intent_id': intent_id, 'intent_name': intent_name})

        check_public_group = db[public_collection].find_one(
            {'_id': ObjectId(group_id)})
        check_private_group = db[private_collection].find_one(
            {'_id': ObjectId(group_id)})

        print('intent_ids after sorting', intent_ids)
        print('intent_names after sorting', intent_names)

        for intent in intents:
            print('intents after sorting', intent)

        if check_public_group is not None:
            db[public_collection].update_one(
                {'_id': ObjectId(group_id)}, {"$set": {"intents": intents, "intent_ids": intent_ids}})

            print('updated successfully in public groups')

            return redirect('/bot-console/groups')
        else:
            db[private_collection].update_one(
                {'_id': ObjectId(group_id)}, {"$set": {"intents": intents, "intent_ids": intent_ids}})

            print('updated successfully in private groups')

            return redirect('/bot-console/groups')

        return redirect('/bot-console/groups')


class delete_group(View):
    def get(self, request, group_id):
        print(group_id)
        user_id = request.user.id
        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        print(client_id)

        # public_collection = 'client{}_public_intents'.format(client_id)
        # private_collection = 'client{}_private_intents'.format(client_id)

        public_groups_collection = 'client{}_public_groups'.format(client_id)
        private_groups_collection = 'client{}_private_groups'.format(client_id)

        bots_collection = 'client{}_bots'.format(client_id)

        db[bots_collection].update_many(
            {}, {"$pull": {'group_ids': group_id}}, True)

        db[bots_collection].update_many(
            {}, {'$pull': {'groups': {'group_id': group_id}}}, True)

        public_group = db[public_groups_collection].find_one(
            {'_id': ObjectId(group_id)})
        private_group = db[private_groups_collection].find_one(
            {'_id': group_id})

        if public_group is not None:
            db[public_groups_collection].remove({'_id': ObjectId(group_id)})

            print("Removed successfully from public groups")

            return HttpResponseRedirect('/bot-console/groups/')

        else:
            db[private_groups_collection].remove({'_id': ObjectId(group_id)})

            print("Removed successfully from private groups")

            return HttpResponseRedirect('/bot-console/groups/')


class Edit_group(View):
    def post(self, request):
        totalMenu = navbar(request.user)
        user_id = request.user.id
        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        private_collection = 'client{}_private_groups'.format(client_id)
        public_collection = 'client{}_public_groups'.format(client_id)

        edited = request.POST['edited']

        if edited == 'false':
            group_id = request.POST['group_id']
            group_private_find = db[private_collection].find_one(
                {'_id': ObjectId(group_id), 'user_id': user_id})
            group_public_find = db[public_collection].find_one(
                {'_id': ObjectId(group_id), 'user_id': user_id, 'clinet_id': client_id})

            if group_private_find is not None:
                group_private_find['id'] = group_private_find['_id']
                return render(request, 'edit/create-group-form.html', {'Menudata': totalMenu, 'username': request.user.username, 'group': group_private_find})

            if group_public_find is not None:
                group_public_find['id'] = group_public_find['_id']
                return render(request, 'edit/create-group-form.html', {'Menudata': totalMenu, 'username': request.user.username, 'group': group_public_find})

        if edited == 'true':
            group_id = request.POST['group_id']

            privacy = request.POST['privacy']

            group_name = request.POST['GroupName']
            group_description = request.POST['GroupDescription']

            print(group_name)

            if privacy == 'private':
                group_find_private = db[private_collection].find_one(
                    {'_id': ObjectId(group_id)})

                if group_find_private is not None:
                    db[private_collection].update_one({'_id': ObjectId(group_id)}, {'$set': {
                        'group_name': group_name, 'group_description': group_description, }}, upsert=True)

                    print('updated successfully in private groups')

                    url = '/edit/edit_group_intent/%s' % group_id

                    return HttpResponseRedirect(url)

                if group_find_private is None:
                    public_group = db[public_collection].find(
                        {'_id': ObjectId(group_id)})

                    db[private_collection].insert_one({'group_name': group_name, 'group_description': group_description,  'created_on': datetime.now(
                    ), 'created_by': request.user.username, 'user_id': user_id, 'client_id': client_id, 'intent_ids': public_group['intent_ids'], 'intents': public_group['intents']})

                    db[public_collection].remove({'_id': ObjectId(group_id)})

                    fetch_group_id = db[private_collection].find_one(
                        {'group_name': group_name, 'user_id': user_id})

                    new_group_id = fetch_group_id['_id']
                    url = '/edit/edit_group_intent/%s' % new_group_id

                    return HttpResponseRedirect(url)

            if privacy == 'public':
                intent_find_public = db[public_collection].find(
                    {'_id': ObjectId(group_id)})

                if intent_find_public is not None:
                    db[public_collection].update_one({'_id': ObjectId(group_id)}, {'$set': {
                        'group_name': group_name, 'group_description': group_description}})

                    url = '/edit/edit_group_intent/%s' % group_id

                    return HttpResponseRedirect(url)

                if intent_find_public is None:
                    db[public_collection].insert_one({'group_name': group_name, 'group_description': group_description, 'created_on': datetime.now(
                    ), 'created_by': request.user.username, 'user_id': user_id, 'client_id': client_id, })

                    db[private_collection].remove({'_id': ObjectId(group_id)})

                    fetch_intent_id = db[public_collection].find_one(
                        {'group_name': group_name, 'user_id': user_id})

                    new_group_id = fetch_group_id['_id']
                    url = '/edit/edit_group_intent/%s' % new_group_id

                    return HttpResponseRedirect(url)


class edit_group_intent(View):
    def get(self, request, group_id):
        totalMenu = navbar(request.user)
        user_id = request.user.id
        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        public_collection = 'client{}_public_groups'.format(client_id)
        private_collection = 'client{}_private_groups'.format(client_id)

        private_group_find = db[private_collection].find_one(
            {'_id': ObjectId(group_id)})
        public_group_find = db[public_collection].find_one(
            {'_id': ObjectId(group_id)})

        # getting all intent of the user

        ##################################################################

        public_intent_collection = 'client{}_public_intents'.format(client_id)
        private_intent_collection = 'client{}_private_intents'.format(
            client_id)

        public_intents = db[public_intent_collection].find()
        private_intents = db[private_intent_collection].find(
            {'user_id': user_id})

        u_public_i = []
        for intent in public_intents:
            intent['id'] = intent['_id']
            u_public_i.append(intent)

        u_private_i = []
        for intent in private_intents:
            intent['id'] = intent['_id']
            u_private_i.append(intent)

        if private_group_find is not None:
            private_group_intents = private_group_find['intents']

            for g_intent in private_group_intents:
                for intent in u_private_i:
                    if g_intent['intent_name'] == intent['intent_name']:
                        print('intent matched')
                        u_private_i.remove(intent)

            return render(request, 'edit/group-intent.html', {'Menudata': totalMenu, 'username': request.user.username, 'intents': private_group_intents, 'final_intents': u_private_i})

        if public_group_find is not None:
            public_group_intents = public_group_find['intents']

            for intent in u_public_i:
                for g_intent in public_group_intents:
                    if g_intent['id'] == intent['id']:
                        u_public_i.remove(intent['id'])
                        continue

            return render(request, 'edit/group-intent.html', {'Menudata': totalMenu, 'username': request.user.username, 'intents': public_group_intents, 'final_intents': u_public_i})

    def post(self, request, group_id):
        print(request.POST)
        # Get request code to display the intents to add them in the group

        user_id = request.user.id

        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        public_collection = 'client{}_public_intents'.format(client_id)
        private_collection = 'client{}_private_intents'.format(client_id)

        public_intents = db[public_collection].find()
        private_intents = db[private_collection].find({'user_id': user_id})

        u_public_i = []
        for intent in public_intents:
            intent['id'] = intent['_id']
            u_public_i.append(intent)

        u_private_i = []
        for intent in private_intents:
            intent['id'] = intent['_id']
            u_private_i.append(intent)

        totalMenu = navbar(request.user)

        #######################################################

        intents = []

        intent_ids = []
        for key in request.POST.keys():
            if 'intent' in key:
                intent_ids.append(request.POST[key])

        if len(intent_ids) <= 0:
            return render(request, 'bots/group-intent.html', {'Menudata': totalMenu, 'username': request.user.username, "public_intents": u_public_i, "private_intents": u_private_i, 'message': 'Please add the intents to the group'})

        intent_names = []

        user_id = request.user.id

        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        public_intents = 'client{}_public_intents'.format(client_id)
        private_intents = 'client{}_private_intents'.format(client_id)

        for intent_id in intent_ids:
            print(intent_id)
            intent_name = db[public_intents].find_one(
                {'_id': ObjectId(intent_id)})
            if intent_name is not None:
                intent_names.append(intent_name['intent_name'])

        for intent_id in intent_ids:
            intent_name = db[private_intents].find_one(
                {'_id': ObjectId(intent_id)})
            if intent_name is not None:
                intent_names.append(intent_name['intent_name'])

        public_collection = 'client{}_public_groups'.format(client_id)
        private_collection = 'client{}_private_groups'.format(client_id)

        for intent_id, intent_name in zip(intent_ids, intent_names):
            intents.append(
                {'intent_id': intent_id, 'intent_name': intent_name})

        check_public_group = db[public_collection].find_one(
            {'_id': ObjectId(group_id)})
        check_private_group = db[private_collection].find_one(
            {'_id': ObjectId(group_id)})

        for intent in intents:
            print('final after sorting', intent)

        if check_public_group is not None:
            db[public_collection].update_one(
                {'_id': ObjectId(group_id)}, {"$set": {"intents": intents, "intent_ids": intent_ids}})

            print('updated successfully in public groups')

            return redirect('/bot-console/groups/')
        else:
            db[private_collection].update_one(
                {'_id': ObjectId(group_id)}, {"$set": {"intents": intents, "intent_ids": intent_ids}})

            print('updated successfully in private groups')

            return redirect('/bot-console/groups/')
