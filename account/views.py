import uuid

from django.contrib.auth import get_user_model
from django.urls import path
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from account import serializers
from account.send_mail import send_confirmation_email
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# from account.send_mail import

User = get_user_model()


class UserViewSet(ListModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (AllowAny,)

    @action(['POST'], detail=False)
    def register(self, request, *args, **kwargs):
        serializer = serializers.RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user:
            try:
                send_confirmation_email(user.email, user.activation_code)
            except Exception as e:
                print(e, '!!!!!!!!!!!!!!!!!!!!!!')
                return Response({'msg': 'Registered, but troubles with email', 'data': serializer.data}, status=201)
        return Response(serializer.data, status=201)

    @action(['GET'], detail=False, url_path='activate/(?P<activation_code>[0-9A-Fa-f-]+)')
    def activate(self, request, activation_code):
        try:
            user = User.objects.get(activation_code=uuid)
        except User.DoesNotExist:
            return Response({'msg': 'Invalid link or link expired!'}, status=400)

        user.is_active = True
        user.activation_code = ''
        user.save()
        return Response({'msg': 'Succesfully activated'}, status=200)


class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)


class RefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)
