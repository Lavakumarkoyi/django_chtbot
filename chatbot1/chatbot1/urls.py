"""chatbot1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from sadmin.views import *
from app.views import *
from django.views.generic import TemplateView
from Management.bots import *
from Management.intents import *
from Management.groups import *
from superadmin.views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    #path("accounts/", include('django.contrib.auth.urls')),
    #path('', TemplateView.as_view(template_name="sadmin/login.html")),
    #path('accounts/login/', TemplateView.as_view(template_name="sadmin/login.html")),
    path('', login.as_view(), name="login"),
    path('accounts/login/', login.as_view(), name="login"),
    path('intents/response-form/<str:intent_id>',
         IntentResponseView.as_view(), name="response_form"),
    # path('sadmin/', include('sadmin.urls')),
    # path('intents/', include('intents.urls')),
    # path('groups/', include('groups.urls')),
    path('bot-console/', include('Management.urls')),
    path('admin/', admin.site.urls),
    path('logout/', logout.as_view()),
    path('chat/<username>/<str:bot_id>', ChatView),
    path('createuser', create_subuser.as_view()),
    path('manageuser', Manageusers.as_view()),
    path('delete_intent/<str:intent_id>', delete_intent.as_view()),
    path('delete_group/<str:group_id>', delete_group.as_view()),
    path('delete_bot/<str:bot_id>', delete_bot.as_view()),
    path('group-intent/<str:group_id>', group_intent.as_view()),
    path('intent-flow/<str:group_id>', intent_flow.as_view()),
    path('group-flow/<str:bot_id>', group_flow.as_view()),
    path('bot-group/<str:bot_id>', bot_group.as_view()),
    path('user-id/inactive-user', Inactive_user.as_view()),
    path('user-id/delete-user', delete_user.as_view()),

    path('edit/', include('Management.urls')),
    path('edit/edit_response/<str:intent_id>', Edit_response.as_view()),
    path('edit/edit_group_intent/<str:group_id>', edit_group_intent.as_view()),
    path('edit/edit_bot_group/<str:bot_id>', Edit_bot_group.as_view()),

    path('superadmin/', clientsView.as_view()),
    path('superadmin/client_details/<str:client_id>', client_details.as_view()),
    #path('complete/', realChat.as_view()),
    path('intent_images', intent_images.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
