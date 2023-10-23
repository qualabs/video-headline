from celery import shared_task
from django.db import models, IntegrityError
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django_fsm import FSMField, transition

from hub_auth.models import Account
from video.models import LiveVideo


class LiveVideoCut(models.Model):
    '''
    Constants to represent the state`s of the Cut
    '''

    class State:
        SCHEDULED = 'scheduled'
        EXECUTING = 'executing'
        PERFORMED = 'performed'
        CHOICES = (
            (SCHEDULED, SCHEDULED),
            (EXECUTING, EXECUTING),
            (PERFORMED, PERFORMED)
        )

    live = models.ForeignKey(LiveVideo,
                             related_name='cuts',
                             verbose_name='Video related to the cut',
                             on_delete=models.CASCADE,
                             )
    initial_time = models.DateTimeField(null=True, blank=True,
                                        verbose_name='Cut start time')
    final_time = models.DateTimeField(null=True, blank=True,
                                      verbose_name='Cut end time')
    description = models.CharField(max_length=200,
                                   default='',
                                   verbose_name='Cut reason'
                                   )
    created_by = models.ForeignKey(Account,
                                   models.SET_NULL,
                                   related_name='uploaded_live_video_cut',
                                   verbose_name='Created by',
                                   null=True)
    state = FSMField(default=State.SCHEDULED,
                     verbose_name='Cut state',
                     choices=State.CHOICES,
                     protected=True)

    def __str__(self):
        return f'{self.live.name} (executed at:{self.initial_time} resumed at:{self.final_time})'

    class Meta:
        verbose_name = 'Live Video Cut'
        verbose_name_plural = 'Live Video Cuts'

    @transition(field=state, source=State.SCHEDULED, target=State.EXECUTING)
    def _to_executing(self):
        pass

    @transition(field=state, source=State.EXECUTING, target=State.PERFORMED)
    def _to_performed(self):
        pass

    def to_executing(self):
        self._to_executing()

        if self.live.state not in [LiveVideo.State.STOPPING, LiveVideo.State.OFF]:
            self.live.to_stopping()

        self.save(update_fields=['state'])

    def to_performed(self):
        self._to_performed()

        if self.live.state not in [LiveVideo.State.STARTING, LiveVideo.State.ON]:
            self.live.to_starting()

        self.save(update_fields=['state'])


@receiver(pre_save, sender=LiveVideoCut, dispatch_uid='pre_save_live_video_cuts')
def live_pre_save_receiver(sender, instance, update_fields, **kwargs):
    if update_fields and 'state' in update_fields:
        return

    if instance.state in [LiveVideoCut.State.PERFORMED]:
        return IntegrityError(
            'The selected cut has already been executed and cannot be modified.'
        )

    instance.initial_time = instance.initial_time.replace(second=0, microsecond=0)
    instance.final_time = instance.final_time.replace(second=0, microsecond=0)

    if not validate_dates(instance):
        raise IntegrityError(
            'There is already a break in the interval entered or the start date is in the past.')


def validate_dates(instance):
    if instance.final_time <= instance.initial_time or \
            (instance.initial_time < timezone.now() and
             instance.state in [LiveVideoCut.State.SCHEDULED]):
        return False

    queryset = LiveVideoCut.objects.filter(live=instance.live,
                                           initial_time__lt=instance.final_time,
                                           final_time__gt=instance.initial_time)
    if instance.id:
        queryset = queryset.exclude(id=instance.id)

    if queryset.count() > 0:
        return False

    return True


@shared_task
def check_live_cuts():
    now = timezone.now()
    cuts_to_off = LiveVideoCut.objects.filter(state=LiveVideoCut.State.SCHEDULED,
                                              initial_time__lte=now)
    cuts_to_on = LiveVideoCut.objects.filter(state=LiveVideoCut.State.EXECUTING,
                                             final_time__lte=now)
    list(map(lambda cut: cut.to_executing(), cuts_to_off))
    list(map(lambda cut: cut.to_performed(), cuts_to_on))
