from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Menu)
admin.site.register(SubMenu)
admin.site.register(client)
admin.site.register(client_user)
admin.site.register(subscription)
admin.site.register(client_subscription)
admin.site.register(spoc_details)
