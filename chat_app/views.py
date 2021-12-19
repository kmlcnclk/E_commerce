from rest_framework.authentication import SessionAuthentication
from django.views.decorators.csrf import csrf_protect, requires_csrf_token, csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
import random
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from rest_framework import status
from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
import jwt
from django.conf import settings
from django.core.exceptions import BadRequest
from rest_framework.response import Response
from chat_app.serializers import MessageSerializer
from Users.models import User
from .models import MessageModel
# Create your views here.
import os
import base64


# bunu imagelara yap
class A(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = None

    def post(self, req):
        image = req.FILES.get('image')
        a = str(base64.b64encode(image.read()))
        name = image.name.split('.')[1]
        b = a.split("b'")[1].replace("'", "")

        return Response(
            f"data:image/{name};base64,{b}"
        )


def send_mail(html=None, text='Email_body', subject='Hello word', from_email='', to_emails=[]):
    assert isinstance(to_emails, list)
    username = 'memethsana24@gmail.com'
    password = 'mh2424..'
    msg = MIMEMultipart('alternative')
    msg['From'] = from_email
    msg['To'] = ", ".join(to_emails)
    msg['Subject'] = subject
    txt_part = MIMEText(text, 'plain')
    msg.attach(txt_part)

    html_part = MIMEText(
        f"<p>Here is your password reset token</p><h1>{html}</h1>", 'html')
    msg.attach(html_part)
    msg_str = msg.as_string()

    server = smtplib.SMTP(host='smtp.gmail.com', port=587)

    server.ehlo()
    print('sa')

    server.starttls()
    server.login(username, password)
    server.sendmail(from_email, to_emails, msg_str)
    server.quit()


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@authentication_classes([])
@permission_classes([])
# @ensure_csrf_cookie
@csrf_protect
def reset_password(req):
    a = req.COOKIES.get('csrftoken')
    # print(request.method)
    # if request.method == 'POST':
    #     reqbody = json.loads(request.body)
    #     token_recieved = reqbody['token']
    #     password = reqbody['password']
    #     password_again = reqbody['password2']
    #     print(request.user)
    #     used = User.objects.get(id=request.user.id)

    #     if token_recieved != used.random_integer:
    #         return Response('Invalid Token')

    #     if password != password_again:
    #         return Response('Passwords should match')
    #     used.random_integer = None
    #     used.save()
    #     return Response('Password changed successfully')

    # token1 = random.randint(100000, 999999)
    # # print(request.user.email)
    # # used = User.objects.get(id=request.user.id)
    # # used.random_integer = token1
    # # used.save()
    # send_mail(html=token1, text='Here is your password reset token',
    #           subject='password reset token', from_email='20212675@std.neu.edu.tr', to_emails=['20212675@std.neu.edu.tr'])

    return Response(a)


class SendMessage(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def post(self, req):
        access = req.headers.get('AUTHORIZATION').split(' ')[1]
        payload = jwt.decode(
            access, settings.SECRET_KEY, algorithms=['HS256'])
        sender_id = payload['user_id']
        username = req.data.get('username')
        message = req.data.get('message')
        if sender_id is not None and username is not None and message is not None:
            user = User.objects.filter(username=username)
            if user.exists():
                data = {
                    'sender_id': sender_id,
                    'receiver_id': user.get().id,
                    'message': message,
                }
                message_serializer = self.serializer_class(data=data)
                if message_serializer.is_valid():
                    message_serializer.save()
                    return Response({'success': True, 'message': 'Message sent'},
                                    status=status.HTTP_201_CREATED)
                else:
                    return Response(message_serializer.errors)
            else:
                raise BadRequest('There is no such user with this username')
        else:
            raise BadRequest(
                'Sender ID or Receiver ID or Message is not defined')


class GetMessages(generics.CreateAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get(self, req):
        username = req.data.get('username')
        access = req.headers.get('AUTHORIZATION').split(' ')[1]
        payload = jwt.decode(
            access, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        if username is not None and user_id is not None:
            user = User.objects.filter(username=username)
            if user.exists():
                list = []
                messages_1 = MessageModel.objects.filter(
                    receiver_id=user_id, sender_id=user.get().id)
                if messages_1.exists():
                    message_serializer_1 = self.serializer_class(
                        messages_1.all(), many=True)
                    if message_serializer_1.data is not None:
                        for i in message_serializer_1.data:
                            list.append(i)
                messages_2 = MessageModel.objects.filter(
                    receiver_id=user.get().id, sender_id=user_id)
                if messages_2.exists():
                    message_serializer_2 = self.serializer_class(
                        messages_2.all(), many=True)
                    if message_serializer_2.data is not None:
                        for a in message_serializer_2.data:
                            list.append(a)

                list.sort(key=lambda x: x['created_at'])

                if list != []:  # bu omazsa list[0] is not None dene.
                    return Response({'success': True, 'data': list}, status=status.HTTP_200_OK)
                else:
                    return Response({'success': True, 'message': 'Message is none'}, status=status.HTTP_200_OK)
            else:
                raise BadRequest('There is no such user with this username')
        else:
            raise BadRequest('Username or User ID is not defined')

# her yere burda ki şeyden yap updated_at


class UpdateMessage(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def put(self, req, message_id):
        access = req.headers.get('AUTHORIZATION').split(' ')[1]
        payload = jwt.decode(
            access, settings.SECRET_KEY, algorithms=['HS256'])
        sender_id = payload['user_id']
        if sender_id is not None:
            user = User.objects.filter(id=sender_id)
            if user.exists():
                msg = req.data.get('message')
                if msg is not None:
                    message = MessageModel.objects.filter(
                        id=message_id, sender_id=sender_id)
                    if message.exists():
                        message_serializer = self.serializer_class(
                            message.get(), many=False)
                        data = {
                            'message': msg,
                            'updated_at': datetime.now()  # her yere bundan ekle
                        }
                        message_serializer = self.serializer_class(
                            message.get(), data=data, partial=True)
                        if message_serializer.is_valid():
                            message_serializer.save()
                            return Response({'success': True, 'message': 'Message is updated'}, status=status.HTTP_200_OK)
                        else:
                            return Response(message_serializer.errors)
                    else:
                        raise BadRequest(
                            'There is no such message or You haven\'t this message')
                else:
                    raise BadRequest('Message field is not defined')
            else:
                raise BadRequest('There is no such user')
        else:
            raise BadRequest('There is no such user')


class DeleteMessage(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def delete(self, req, message_id):
        access = req.headers.get('AUTHORIZATION').split(' ')[1]
        payload = jwt.decode(
            access, settings.SECRET_KEY, algorithms=['HS256'])
        sender_id = payload['user_id']
        if sender_id is not None:
            user = User.objects.filter(id=sender_id)
            if user.exists():
                message = MessageModel.objects.filter(
                    id=message_id, sender_id=sender_id)
                if message.exists():
                    message.delete()
                    return Response({'success': True, 'message': 'Message is deleted'}, status=status.HTTP_200_OK)
                else:
                    raise BadRequest(
                        'There is no such message or You haven\'t this message')
            else:
                raise BadRequest('There is no such user')
        else:
            raise BadRequest('There is no such user')
