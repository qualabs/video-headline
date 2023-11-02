from django.db import models

from organization.models import Channel, Organization


class Tag(models.Model):
    name = models.CharField(max_length=254, verbose_name='Name')
    organization = models.ForeignKey(
        Organization,
        models.CASCADE,
        null=True,
        related_name='tags',
        verbose_name='Organization',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        unique_together = [['name', 'organization']]
