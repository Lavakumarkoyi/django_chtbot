from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Menu(models.Model):
    MenuName = models.CharField(max_length=20, primary_key=True)
    MenuIcon = models.CharField(max_length=20)
    userAccess = models.CharField(max_length=255, null=True, blank=True)


class SubMenu(models.Model):
    Menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    SubMenuName = models.CharField(max_length=20)
    Link = models.CharField(max_length=255)

# clientadmin and user relationship Model


class spoc_details(models.Model):
    spoc_name = models.CharField(max_length=255)
    spoc_email = models.CharField(max_length=50)
    spoc_mobile = models.IntegerField()


class subscription(models.Model):
    subscription_name = models.CharField(max_length=255)
    number_of_bots = models.CharField(max_length=50)
    number_of_groups = models.CharField(max_length=50)
    number_of_intents = models.CharField(max_length=50)
    number_of_subAccounts = models.CharField(max_length=50)
    number_of_interaction = models.CharField(max_length=50)
    billing_type = models.CharField(max_length=255)


class client_subscription(models.Model):
    subscription_id = models.ForeignKey(subscription, on_delete=models.CASCADE)
    subscription_start_date = models.DateTimeField()
    subscription_end_date = models.DateTimeField()


class client(models.Model):
    client_name = models.CharField(max_length=50, unique=True)
    client_logo = models.URLField(max_length=255, null=True, blank=True)
    client_added = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    spoc_details = models.ForeignKey(
        spoc_details, on_delete=models.CASCADE)
    subscription_id = models.ForeignKey(
        subscription, on_delete=models.CASCADE)


class client_user(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    client_id = models.ForeignKey(client, on_delete=models.CASCADE)
    is_delete = models.BooleanField(default=False)
