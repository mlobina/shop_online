from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet

from .serializers import UserSerializer, AuthTokenSerializer, ContactSerializer
from core.models import Contact


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user


class ContactViewSet(ModelViewSet):
    """Manage contacts in the database"""
    throttle_scope = 'user'
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ContactSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = Contact.objects.all()
        else:
            queryset = Contact.objects.filter(user=self.request.user.id)
        return queryset












