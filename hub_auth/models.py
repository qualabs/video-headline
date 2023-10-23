from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from secrets import token_hex

from organization.models import Organization


class Account(AbstractUser):
    organization = models.ForeignKey(
        Organization,
        related_name='users',
        on_delete=models.CASCADE,
        verbose_name='Organization',
        null=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


# New model to extract Group from django auth app to ours.
class GroupProxy(Group):
    class Meta:
        # Does not generate other table in the db.
        proxy = True
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'


def get_key():
    return token_hex(48)


class APIKey(models.Model):
    name = models.CharField(max_length=254,
                            blank=True,
                            verbose_name='Name')

    account = models.ForeignKey(Account,
                                on_delete=models.CASCADE,
                                related_name='api_keys',
                                verbose_name='User')

    api_key = models.CharField(max_length=100,
                               verbose_name='api key',
                               default=get_key)

    def __str__(self):
        return str(self.name)
