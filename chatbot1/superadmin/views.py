from django.shortcuts import render, redirect
from django.views.generic import View
from sadmin.models import *

# Create your views here.


class clientsView(View):
    def get(self, request):
        subscription_details = subscription.objects.all()
        clients = client.objects.all()
        return render(request, 'superadmin/clients.html', {'clients': clients, 'subscriptions': subscription_details})

    def post(self, request):

        if request.POST['formdata'] == 'clients':
            client_id = request.POST['client_id']
            url = '/superadmin/client_details/%s' % client_id

            return redirect(url)

        if request.POST['formdata'] == 'subscription':
            print(request.POST)

        if request.POST['formdata'] == 'addClient':
            client_name = request.POST['client_name']
            


class client_details(View):
    def get(self, request, client_id):
        print(client_id)
        print('entered into client details')
        c_details = client.objects.get(id=client_id)

        print(c_details.id)
        print(c_details.subscription_id.id)

        subscription_details = subscription.objects.get(
            id=c_details.subscription_id.id)

        client_subscription_details = client_subscription.objects.get(
            subscription_id=c_details.subscription_id.id)

        spoc_details_1 = spoc_details.objects.get(id=c_details.spoc_details.id)

        return render(request, 'superadmin/client_details.html', {'client_details': c_details, 'subscription_details': subscription_details, 'spoc_details': spoc_details_1})
