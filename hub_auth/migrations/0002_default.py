# Generated by Django 2.1.5 on 2023-11-22 17:56

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import hub_auth.models
import boto3
import os 
import json 
import re
import utils.s3
import utils.cloudfront

class Migration(migrations.Migration):

    initial = True
    #define variables for using in the migrations class 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.media_convert_role_arn = os.getenv('AWS_MEDIA_CONVERT_ROLE')
        self.media_live_role_arn = os.getenv('AWS_MEDIA_LIVE_ROLE')
        self.account_id = self.media_convert_role_arn.split(':')[4]
        self.configuration_folder = os.path.join(os.path.dirname(__file__), 'configuration.samples/')
    
    
    def assign_user_to_organization(apps, schema_editor):
        User = apps.get_model('hub_auth', 'account')
        Organization = apps.get_model('organization', 'Organization')
        django_session = apps.get_model('django', 'Session')
        # get current user logged in 
        session = django_session.objects.get(
            expire_date__gte=django.utils.timezone.now()
        )
        user = User.objects.get(
            pk=session.get_decoded().get('_auth_user_id')
        )
        #is there a way of knowing which is the user logged in ?
        organization = Organization.objects.get(
            name='Default Organization'
        )
        user.organization = organization
        user.save()
    

            
    def create_AWS_Account(self,apps, schema_editor):
        aws_account = apps.get_model('organization', 'AWSAccount')
        media_convert_endpoint_url = self.get_media_convert_endpoint_url()
        aws_default_region = os.environ.get('AWS_DEFAULT_REGION')

        aws_account_defaults = {
            'name': 'Default AWS Account',
            'access_key': Migration.aws_access_key_id,
            'secret_access_key': Migration.secret_access_key,
            'media_live_role': Migration.media_live_role_arn,
            'media_convert_role': Migration.media_convert_role_arn,
            'region': aws_default_region,
            'account_id': Migration.account_id,
            'media_convert_endpoint_url': media_convert_endpoint_url,
        }
        return aws_account.objects.create(**aws_account_defaults).id

    def test(self,apps, schema_editor):
        return self.create_global_settings(apps, schema_editor)
        
    def create_global_settings(self,apps, schema_editor):
        configuration_model = apps.get_model('configuration', 'configuration')
        file_path = os.path.join(self.configuration_folder,'cloud_front_configuration.json')
        if not os.path.exists(file_path):
            return
        
        with open(file_path) as json_file:
            cloud_front_configuration = {
                "cloud_front_configuration":json.load(json_file)
            }
        
        configuration_model.objects.create(**cloud_front_configuration)
            
        
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
        media_convert_settings_id = Migration.create_default_media_convert_settings(apps, schema_editor)
        plan_default = {"name":'Default Plan',
                            "medialive_configuration_id": Migration.create_default_media_live_settings(apps, schema_editor),
                            "video_transcode_configuration_id":media_convert_settings_id,
                            "audio_transcode_configuration_id" : media_convert_settings_id
                        }
                    
        return plan.objects.create( **plan_default).id
        
    def create_organization(apps, schema_editor):
        organization = apps.get_model('organization', 'organization')
        bucket_name = utils.s3.generate_bucket_name('Default Organization')
        aws_account = apps.get_model('organization', 'AWSAccount')
        aws_account_id = Migration.create_AWS_Account(apps, schema_editor)
        aws_account_dict = aws_account()
        aws_account_dict.name = 'Default AWS Account'
        aws_account_dict.access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_account_dict.secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        organizacion_dict = organization()
        organizacion_dict.bucket_name = bucket_name
        organizacion_dict.aws_account_id =aws_account_id
        organizacion_dict.name = 'Default Organization'
        utils.s3.create_bucket(organizacion_dict)
        organization_default ={"name":'Default Organization',
                               "contact_email":'Default Organization@default.com',
                               "bucket_name":bucket_name,
                               "aws_account_id":aws_account_id,
                               "plan_id": Migration.create_plan(apps, schema_editor)}
        organization.objects.create(**organization_default)
            

    def create_periodic_tasks(apps, schema_editor):
        PeriodicTask = apps.get_model('djcelery', 'PeriodicTask')
        PeriodicTask.objects.create(
            name='Delete Channels',
            task='hub.tasks.delete_channels',
            interval=3600,
            enabled=True,
        )
        PeriodicTask.objects.create(
            name='Delete Inputs',
            task='hub.tasks.delete_inputs',
            interval=3600,
            enabled=True,
        )
        PeriodicTask.objects.create(
            name='Check Live Cuts',
            task='hub.tasks.check_live_cuts',
            interval=60,
            enabled=True,
        )
        PeriodicTask.objects.create(
            name='Delete Distributions',
            task='hub.tasks.delete_distributions',
            interval=86400,
            enabled=True,
        )
        PeriodicTask.objects.create(
            name='Bill Renewal',
            task='hub.tasks.bill_renewal',
            interval=2592000,
            enabled=True,
        )
    
        
    def get_media_convert_endpoint_url(self):
        mediaconvert_client = boto3.client('mediaconvert', 
                                           aws_access_key_id=Migration.access_key_id,
                                           aws_secret_access_key=Migration.secret_access_key,
                                           region_name=Migration.aws_default_region)
        
        try:
            return mediaconvert_client.describe_endpoints()['Endpoints'][0]['Url']
        except Exception as e:
            return None


    dependencies = [
        ('organization', '0001_initial'),
        ('auth', '0009_alter_user_last_name_max_length'),
        ('hub_auth', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(test),
        migrations.RunPython(create_AWS_Account),
        # migrations.RunPython(create_organization),
        # migrations.RunPython(assign_user_to_organization),
        # migrations.RunPython(create_periodic_tasks),

    ]
