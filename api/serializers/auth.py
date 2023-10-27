from rest_framework import serializers

from hub_auth.models import Account
from .organization import OrganizationSerializer


class AccountSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()

    class Meta:
        model = Account
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'organization',
        )


class MinAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            'id',
            'username',
        )


class ChangeAccountPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    new_password_2 = serializers.CharField()

    def validate(self, data):
        new_password = data['new_password']
        new_password_2 = data['new_password_2']

        if new_password == new_password_2:
            return data
        else:
            raise serializers.ValidationError(
                'The new password must be the same in both fields, please'
                'verify.'
            )
