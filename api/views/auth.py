from django.contrib.auth import login
from rest_framework import viewsets, permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from knox.views import LoginView as KnoxLoginView
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions

from api.exceptions import WrongPassword
from hub_auth.models import Account
from api.serializers import AccountSerializer, ChangeAccountPasswordSerializer
from api.permissions import OnlySuperusersPermission


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        self.serializer = AuthTokenSerializer(data=request.data)
        serializer = self.serializer
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None)


class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = (OnlySuperusersPermission,)
    queryset = Account.objects.prefetch_related('organization').all().order_by('id')

    def get_serializer_class(self):
        serializer_class = {
            'change_password': ChangeAccountPasswordSerializer,
        }

        if self.action and self.action in serializer_class.keys():
            return serializer_class[self.action]
        else:
            return self.serializer_class

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = self.get_serializer(self.request.user)
        return Response(user.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.request.user
        old_password = serializer.validated_data['old_password']

        if not user.check_password(old_password):
            raise WrongPassword()

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response()
