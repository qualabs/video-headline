import sys
from django.contrib import admin
from solo.admin import SingletonModelAdmin

from configuration.models import Configuration, MediaConvertConfiguration, MediaLiveConfiguration


@admin.register(Configuration)
class ConfigAdmin(SingletonModelAdmin):
    pass


# Create the singleton object if does not exists
if len(sys.argv) > 1 and not sys.argv[1] in ['makemigrations', 'migrate', 'collectstatic']:
    config = Configuration.get_solo()


@admin.register(MediaConvertConfiguration)
class MediaConvertAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')


@admin.register(MediaLiveConfiguration)
class MediaLiveAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')