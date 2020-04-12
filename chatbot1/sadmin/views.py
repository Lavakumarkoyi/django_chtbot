from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import permission_classes
from .models import client, client_user, Menu, SubMenu
from django.db.models import Q
from datetime import datetime
from django.http import HttpResponseRedirect

import pymongo
from bson.objectid import ObjectId
Mongoclient = pymongo.MongoClient("localhost", 27017)

db = Mongoclient.chatbot


# Create your views here


class login(APIView):
    permission_classes = (AllowAny,)
    # registered = False

    def get(self, request):
        return render(request, 'sadmin/login.html')

    def post(self, request):
        registered = request.POST['registered']
        # print(registered)
        if registered == 'false':
            emailId = request.POST['email']
            try:
                users = User.objects.filter(email=emailId)
                print(users)
                if users is not None:
                    for i in users:
                        c_user = client_user.objects.get(user_id_id=i.id)
                        if c_user.is_delete is False:
                            user = i
                if user is None:
                    return render(request, 'sadmin/login.html', {
                        'message': 'USER DOESNOT EXIST'
                    })
            except Exception as e:
                # print("Exception of email", e)
                return render(request, 'sadmin/login.html', {
                    'message': 'USER DOESNOT EXIST'
                })

            client_id = client_user.objects.get(
                user_id_id=user.id).client_id_id

            print(client_id)

            client_info = client.objects.get(id=client_id)
            print(client_info)

            if client_info.is_active:
                if user.is_active:
                    return render(request, 'sadmin/password.html', {
                        'userName': user.username
                    })
                else:
                    return render(request, 'sadmin/login.html', {
                        'message': 'USER IS NOT ACTIVE'
                    })
            else:
                return render(request, 'sadmin/login.html', {
                    'message': 'USER CLIENT IS NOT ACTIVE'
                })

        if registered == 'true':
            username = request.POST['email']
            password = request.POST['password']

            print(username, password)
            user = authenticate(username=username, password=password)
            # print(user)

            if user is not None:
                auth_login(request, user)
                print("user logged in successfully")
                return redirect('/bot-console/bots')
            else:
                return render(request, 'sadmin/password.html', {
                    'message': 'PASSWORD IS INCORRECT',
                    'userName': username
                })


def navbar(user):
    totalMenu = []
    if user.is_staff:
        MenuItems = Menu.objects.filter(
            Q(userAccess='is_active') | Q(userAccess='is_staff'))
        for MenuItem in MenuItems:
            subMenuItems = SubMenu.objects.all().prefetch_related(
                'Menu').filter(Menu_id=MenuItem.MenuName).values()
            data = {
                "MenuItem": MenuItem,
                "SubMenuItem": subMenuItems
            }

            for subMenuItem in subMenuItems:
                totalMenu.append(subMenuItem)

        print("Menu Items", totalMenu)
    else:
        MenuItems = Menu.objects.filter(userAccess='is_active')
        for MenuItem in MenuItems:
            subMenuItems = SubMenu.objects.all().prefetch_related(
                'Menu').filter(Menu_id=MenuItem.MenuName)
            data = {
                "MenuItem": MenuItem,
                "SubMenuItem": subMenuItems
            }

            for subMenuItem in subMenuItems:
                totalMenu.append(subMenuItem)

    return totalMenu


class logout(View):
    def get(self, request):
        auth_logout(request)
        return redirect('/')


class create_subuser(View):
    @permission_classes((IsAuthenticated, IsAdminUser))
    @method_decorator(login_required)
    def get(self, request):
        if request.user.is_staff:
            totalMenu = navbar(request.user)
            return render(request, 'sadmin/registration.html', {'username': request.user.username, 'Menudata': totalMenu})

    def post(self, request):
        userdata = request.POST
        totalMenu = navbar(request.user)
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password1 = request.POST['password1']

        if get_user_model().objects.filter(username=username).exists():
            return render(request, 'sadmin/registration.html', {'message': 'User already exists', 'username': request.user.username, 'Menudata': totalMenu, 'formData': userdata})
        elif get_user_model().objects.filter(email=email).exists():
            count = 0
            users = get_user_model().objects.filter(email=email)
            if users is not None:
                for user in users:
                    if client_user.objects.get(user_id_id=user.id).is_delete is False:
                        count = count + 1

            if count > 0:
                return render(request, 'sadmin/registration.html', {'message': 'email already exists', 'username': request.user.username, 'Menudata': totalMenu, 'formData': userdata})
            elif password != password1:
                return render(request, 'sadmin/registration.html', {'message': 'Password not match', 'username': request.user.username, 'Menudata': totalMenu, 'formData': userdata})
            else:
                u = get_user_model().objects.create_user(email=email, username=username)
                u.set_password(password)
                u.save()

                print(request.user.id)

                client_id = client_user.objects.filter(
                    user_id_id=request.user.id)[0]
                print(client_id.client_id_id)
                print('client_id fetched')

                user_addedNow = get_user_model().objects.filter(
                    username=username)[0]

                print(user_addedNow.id)

                print('user id is fetched')

                p = client_user(client_id_id=client_id.client_id_id,
                                user_id_id=user_addedNow.id)
                p.save()
                print('user created and user created with relation to client')

                return render(request, 'sadmin/registration.html', {'message': 'user created successfully', 'Menudata': totalMenu, 'username': request.user.username})
        elif password != password1:
            return render(request, 'sadmin/registration.html', {'message': 'Password not match', 'username': request.user.username, 'Menudata': totalMenu, 'formData': userdata})
        else:
            u = get_user_model().objects.create_user(email=email, username=username)
            u.set_password(password)
            u.save()

            print(request.user.id)

            client_id = client_user.objects.filter(
                user_id_id=request.user.id)[0]
            print(client_id.client_id_id)
            print('client_id fetched')

            user_addedNow = get_user_model().objects.filter(
                username=username)[0]

            print(user_addedNow.id)

            print('user id is fetched')

            p = client_user(client_id_id=client_id.client_id_id,
                            user_id_id=user_addedNow.id)
            p.save()
            print('user created and user created with relation to client')

            return render(request, 'sadmin/registration.html', {'message': 'user created successfully', 'Menudata': totalMenu, 'username': request.user.username})


class Manageusers(View):
    @method_decorator(login_required)
    def get(self, request):
        if request.user.is_staff:
            print("logged in user", request.user)
            print("logged in user id", request.user.id)
            client_id = client_user.objects.filter(
                user_id_id=request.user.id)[0].client_id_id
            print(client_id)

            users_under_client = client_user.objects.filter(
                client_id_id=client_id).values()
            print(users_under_client)

            user_ids = []

            for i in users_under_client:
                print(i)
                user_ids.append(i['user_id_id'])

            print(user_ids)

            Manage_user_list = []

            for i in user_ids:
                user = User.objects.get(id=i)
                a = client_user.objects.get(user_id_id=i)
                if a.is_delete:
                    continue
                Manage_user_list.append(user)
            print(Manage_user_list)

            totalMenu = navbar(request.user)
            return render(request, 'sadmin/data_List.html', {'Menudata': totalMenu, 'username': request.user.username, 'users': Manage_user_list})


class Inactive_user(View):
    def post(self, request):
        totalMenu = navbar(request.user)
        user_id = request.POST["user_id"]
        activity = request.POST['activity']

        print("POST DATA", request.POST)

        print("is inactive or active", activity, "registered user id", user_id)

        if activity == 'active':
            a = User.objects.get(id=user_id)
            a.is_active = False
            a.save()

            return redirect('/manageuser')

        elif activity == 'inactive':
            b = User.objects.get(id=user_id)
            b.is_active = True
            b.save()

        return redirect('/manageuser')


class delete_user(View):
    def post(self, request):
        print("delete POST DATA", request.POST)
        user_id = request.POST['user_id']
        print(user_id)
        transfer_id = request.POST['user_transfer']
        transfer_user = get_user_model().objects.get(id=transfer_id).username

        print("intents transfer to", transfer_user, transfer_id)

        client_id = client_user.objects.get(user_id_id=user_id).client_id_id

        public_groups = 'client{}_public_groups'.format(client_id)
        private_groups = 'client{}_private_groups'.format(client_id)

        public_intents = 'client{}_public_intents'.format(client_id)
        private_intents = 'client{}_private_intents'.format(client_id)

        client_bots = 'client{}_bots'.format(client_id)

        pu_groups = db[public_groups].find({'user_id': user_id})

        pr_groups = db[private_groups].find({'user_id': user_id})

        pu_intents = db[public_intents].find({'user_id': user_id})

        pr_intents = db[private_intents].find({'user_id': user_id})

        p_bots = db[client_bots].find({'user_id': user_id})

        if pu_groups:
            db[public_groups].update_many(
                {'user_id': user_id}, {'$set': {'user_id': transfer_id, 'transferred_to': transfer_user}}, True)

            print("public groups updated")
        if pr_groups:
            db[private_groups].update_many(
                {'user_id': user_id}, {'$set': {'user_id': transfer_id, 'transferred_to': transfer_user}}, True)

            print('private groups update')

        if pu_intents:
            db[public_intents].update_many(
                {'user_id': user_id}, {'$set': {'user_id': transfer_id, 'transferred_to': transfer_user}}, True)

            print('public intents update')

        if pr_intents:
            db[private_intents].update_many(
                {'user_id': user_id}, {'$set': {'user_id': transfer_id, 'transferred_to': transfer_user}}, True)

            print('private intents update')

        if p_bots:
            db[client_bots].update_many(
                {'user_id': user_id}, {'$set': {'user_id': transfer_id, 'transferred_to': transfer_user}}, True)

            print('bots update')

        a = get_user_model().objects.get(id=user_id)
        a.username = str(user_id) + 'del' + '963258741'
        a.is_active = False
        a.save()

        b = client_user.objects.get(user_id_id=user_id)
        b.is_delete = True
        b.save()

        return redirect('/manageuser')


"""def logout(request):
    print("Logout :", request)
    # logout(request)
    return redirect('/')"""
