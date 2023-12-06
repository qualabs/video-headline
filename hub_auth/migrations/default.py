# Generated by Django 2.1.5 on 2023-11-22 17:56

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import boto3
import os 
import json 

class Migration(migrations.Migration):

    initial = True
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    media_convert_role_arn = os.getenv('AWS_MEDIA_CONVERT_ROLE')
    media_live_role_arn = os.getenv('AWS_MEDIA_LIVE_ROLE')
    media_convert_endpoint_url = os.getenv('AWS_MEDIA_CONVERT_ENDPOINT')
    account_id = media_convert_role_arn.split(':')[4]
    aws_default_region = os.environ.get('AWS_DEFAULT_REGION')
    configuration_folder = os.path.join(os.path.dirname(__file__), 'configuration.samples/')
      
    def create_AWS_Account(apps, schema_editor):
        aws_account = apps.get_model('organization', 'AWSAccount')
        media_convert_endpoint_url = Migration.media_convert_endpoint_url if Migration.media_convert_endpoint_url else Migration.get_media_convert_endpoint_url()
        aws_default_region = os.environ.get('AWS_DEFAULT_REGION')

        aws_account_defaults = {
            'name': 'Default AWS Account',
            'access_key': Migration.aws_access_key_id,
            'secret_access_key': Migration.aws_secret_access_key,
            'media_live_role': Migration.media_live_role_arn,
            'media_convert_role': Migration.media_convert_role_arn,
            'region': aws_default_region,
            'account_id': Migration.account_id,
            'media_convert_endpoint_url': media_convert_endpoint_url,
        }
        return aws_account.objects.create(**aws_account_defaults).id


        
    def create_global_settings(apps, schema_editor):
        from configuration.models import Configuration as configuration_model
        config = configuration_model()
        
        
        file_path = os.path.join(Migration.configuration_folder,'cloud_front_configuration.json')
        if not os.path.exists(file_path):
            return
        
        with open(file_path) as json_file:
            config.cloud_front_configuration = json.load(json_file)
        
        
        config.save()
            
        
    def create_default_media_convert_settings(apps, schema_editor):
        media_convert = apps.get_model('configuration', 'MediaConvertConfiguration')
        file_path = os.path.join(Migration.configuration_folder, 'media_convert_configuration.json')
        media_convert_configuration = {}
        with open(file_path) as json_file:
            media_convert_configuration = json.load(json_file)
        
        media_convert_default = {"name" : "Default Media Convert Configuration",
                                 "description" : "Default Media Convert Configuration",
                                "settings" : media_convert_configuration}
        
        return media_convert.objects.create(**media_convert_default).id
        
        
    def create_default_media_live_settings(apps, schema_editor):
        media_live_configuration = apps.get_model('configuration', 'MediaLiveConfiguration')
        file_path_encoder_settings = os.path.join(Migration.configuration_folder, 'media_live_encoder_settings.json')
        file_path_source_settings = os.path.join(Migration.configuration_folder, 'media_live_input_attachments.json')
        file_path_destination_settings = os.path.join(Migration.configuration_folder, 'media_live_destinations.json')
        media_live_encoder_settings_configuration = {}
        media_live_source_settings_configuration = {}
        media_live_destination_settings_configuration = {}
        with open(file_path_encoder_settings) as json_file:
            media_live_encoder_settings_configuration = json.load(json_file)
        with open(file_path_source_settings) as json_file:
            media_live_source_settings_configuration = json.load(json_file)
        with open(file_path_destination_settings) as json_file:
            media_live_destination_settings_configuration = json.load(json_file)
        
        media_live_default = {"name" : "Default Media Live Configuration",
         "description" : "Default Media Live Configuration",
         "source_settings" : media_live_source_settings_configuration,
         "destination_settings" : media_live_destination_settings_configuration,
         "encoder_settings" : media_live_encoder_settings_configuration}
        
        return media_live_configuration.objects.create(**media_live_default).id
        
    def create_plan(apps, schema_editor):
        plan = apps.get_model('organization', 'Plan')
        plan_default = plan.objects.filter(name='Default Plan')
        if plan_default.exists():
            return plan_default[0].id
        else :
            from organization.models import Plan
            media_convert_settings_id = Migration.create_default_media_convert_settings(apps, schema_editor)
            new_plan = Plan()
            new_plan.name = 'Default Plan'
            new_plan.id = 1
            new_plan.medialive_configuration_id = Migration.create_default_media_live_settings(apps, schema_editor)
            new_plan.video_transcode_configuration_id = media_convert_settings_id
            new_plan.audio_transcode_configuration_id = media_convert_settings_id
            new_plan.save()
                        
            return new_plan.id
        
    def create_organization(apps, schema_editor):
        aws_account = apps.get_model('organization', 'AWSAccount')
        aws_account_id = Migration.create_AWS_Account(apps, schema_editor)
        aws_account_dict = aws_account()
        aws_account_dict.name = 'Default AWS Account'
        aws_account_dict.access_key =Migration.aws_access_key_id
        aws_account_dict.secret_access_key = Migration.aws_secret_access_key
        
        from organization.models import Organization
        import math
        import time
        new_organization = Organization()
        new_organization.name = f'Default Organization{math.floor(time.time())}'
        new_organization.plan_id = Migration.create_plan(apps, schema_editor)
        new_organization.aws_account_id = aws_account_id
        new_organization.id = 1
        new_organization.save()
            
    def add_interval_schedule(apps, schema_editor, seconds):
        IntervalSchedule = apps.get_model('django_celery_beat', 'IntervalSchedule')
        return IntervalSchedule.objects.create(
            every=seconds,
            period='seconds',
        )
        

    def create_periodic_tasks(apps, schema_editor):
        PeriodicTask = apps.get_model('django_celery_beat', 'PeriodicTask')
        PeriodicTask.objects.create(
            name='Delete Channels ',
            task='hub.tasks.delete_channels',
            interval=Migration.add_interval_schedule(apps, schema_editor, 3600),
            enabled=False,
        )
        PeriodicTask.objects.create(
            name='Delete Inputs',
            task='hub.tasks.delete_inputs',
            interval=Migration.add_interval_schedule(apps, schema_editor, 3600),
            enabled=False,
        )
        PeriodicTask.objects.create(
            name='Check Live Cuts',
            task='hub.tasks.check_live_cuts',
            interval=Migration.add_interval_schedule(apps, schema_editor, 60),
            enabled=False,
        )
        PeriodicTask.objects.create(
            name='Delete Distributions',
            task='hub.tasks.delete_distributions',
            interval=Migration.add_interval_schedule(apps, schema_editor, 86400),
            enabled=False,
        )
        PeriodicTask.objects.create(
            name='Bill Renewal',
            task='hub.tasks.bill_renewal',
            interval=Migration.add_interval_schedule(apps, schema_editor, 86400),
            enabled=False,
        )
        
    
        
    def get_media_convert_endpoint_url():
        mediaconvert_client = boto3.client('mediaconvert', 
                                           aws_access_key_id=Migration.aws_access_key_id,
                                           aws_secret_access_key=Migration.aws_secret_access_key,
                                           region_name=Migration.aws_default_region)
        
        try:
            return mediaconvert_client.describe_endpoints()['Endpoints'][0]['Url']
        except Exception as e:
            return None

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
        ('hub_auth', '0001_initial'),
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_global_settings),
        migrations.RunPython(create_organization),
        migrations.RunPython(create_periodic_tasks),     
    ]
