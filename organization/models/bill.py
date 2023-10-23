from django.utils import timezone

from django.db import models
from jsonfield import JSONField
from organization.models import Organization, Plan


class Bill(models.Model):
    organization = models.ForeignKey(Organization,
                                     models.CASCADE,
                                     related_name='bills',
                                     verbose_name='Organization')
    plan = models.ForeignKey(Plan,
                             models.PROTECT,
                             null=True,
                             default=None,
                             related_name='bills',
                             verbose_name='Plan')
    date = models.DateField(verbose_name='Creation Date')
    last_modified = models.DateTimeField(auto_now=True,
                                         verbose_name='Updated Date')
    video_transcoding = models.FloatField(default=0,
                                          verbose_name='Video Transcoding Minutes')
    audio_transcoding = models.FloatField(default=0,
                                          verbose_name='Audio Transcoding Minutes')
    storage = models.FloatField(default=0,
                                verbose_name='Storage (GB)')
    data_transfer = models.FloatField(default=0,
                                      verbose_name='Traffic (GB)')
    extras = JSONField(blank=True,
                       default=dict,
                       verbose_name='Extra information')

    def __str__(self):
        date = self.date.strftime('%b-%Y')
        return f'{self.organization.name} - {date}'

    class Meta:
        verbose_name = 'Usage Report'
        verbose_name_plural = 'Usage Reports'
        unique_together = ('date', 'organization')

    def save(self, *args, **kwargs):
        self.date = self.date.replace(day=1)
        super(Bill, self).save(*args, **kwargs)

    def is_current_bill(self):
        today = timezone.now()
        return (today.year == self.date.year) and (today.month == self.date.month)
