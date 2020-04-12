from django.conf.urls import url
from .views import *

urlpatterns = [
    url('', clientsView.as_view(), name="clients"),
]
