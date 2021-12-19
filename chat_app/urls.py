from django.urls import path
from .views import SendMessage, GetMessages, UpdateMessage, DeleteMessage, A, reset_password, reset_passworda

urlpatterns = [
    path('send_message', SendMessage.as_view(), name='send_message'),
    path('get_messages', GetMessages.as_view(), name='get_message'),
    path('update_message/<str:message_id>',
         UpdateMessage.as_view(), name='update_message'),
    path('delete_message/<str:message_id>',
         DeleteMessage.as_view(), name='delete_message'),
    path('a', A.as_view(), name='a'),
    path('r', reset_password, name='r'),
    path('ra', reset_passworda, name='ra'),
]
