# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from base64 import b64decode

import re
from django.conf import settings
from django.http import Http404
from django.utils.safestring import mark_safe
from django.views.generic.base import TemplateView

from video.models import Media, LiveVideo


class EmbedView(TemplateView):
    template_name = "player/index.html"

    def validate_domain(self, channel_allowed_domains, referer_domain):
        allowed_domains = settings.ALLOWED_DOMAINS + channel_allowed_domains

        if len(channel_allowed_domains) == 0:
            return True

        for allowed_domain in allowed_domains:
            secondary = allowed_domain
            allowed_domain = re.escape(allowed_domain).replace('\\*', '[a-zA-Z0-9_-]+')
            allowed_domain = re.compile(allowed_domain)
            if allowed_domain.match(str(referer_domain)):
                return True

        return False

    def get_context_data(self, **kwargs):
        context = super(EmbedView, self).get_context_data(**kwargs)

        poster_url, video, video_url, mime_type = self.get_video_data(kwargs.get('video_id'))
        channel = video.channel
        organization = video.organization

        if not organization.traffic_enabled:
            context['error'] = True
            context['message'] = 'The content is not available.'
            return context

        referer = self.request.META.get('HTTP_REFERER')

        referer_domain = None
        if referer:
            regex_domain = r'^(?:https?:\/\/)?(?:[^@\/\n]+@)?([^:\/?\n]+)'
            referer_domain = re.match(regex_domain, referer).group(1)

        adTagUrl = mark_safe(
            video.ads_vast_url or channel.ads_vast_url or ''
        ) if video.enable_ads else mark_safe('')

        if video.autoplay == 'c':
            autoplay = channel.autoplay
        else:
            autoplay = video.autoplay == 'y'

        if not autoplay:
            autoplay = ''

        if self.validate_domain(channel.allowed_domains, referer_domain):
            if video.state not in [LiveVideo.State.ON, Media.State.FINISHED]:
                context['error'] = True
                context['message'] = 'The content is not available.'

                return context

            else:
                video_data = {
                    'error': False,
                    'url': video_url,
                    'type': mime_type,
                    'laUrl': '',
                    'laType': '',
                    'certUrl': '',
                    'adTagUrl': adTagUrl,
                    'posterUrl': poster_url,
                    'autoplay': autoplay,
                    'tracking_api_url': '',
                    'player_api_key': '',
                    'qhub_analytics_enabled': '',
                    'qhub_analytics_plugin_url': '',
                    'channel': channel,
                    'organization': organization,
                    'video': video,
                    'playerCustomCss': ''
                }
                if self.request.GET.get('token'):
                    video_data['token'] = b64decode(self.request.GET.get('token').encode('utf-8')).decode('utf-8')

                # Traking
                org_qtracking_config = organization.config.get('qtracking')

                if org_qtracking_config:
                    player_api_key = org_qtracking_config.get('player_api_key')
                    tracking_api_url = org_qtracking_config.get('tracking_api_url')
                    tracking_enabled = org_qtracking_config.get('enabled')

                    if player_api_key and tracking_enabled and tracking_api_url:
                        video_data['player_api_key'] = player_api_key
                        video_data['tracking_api_url'] = f'{tracking_api_url}/api/v1/tracking/'

                custom_player_css = organization.config.get('playerCustomCss')

                if custom_player_css: video_data['playerCustomCss'] = custom_player_css

                # Qhub analytics
                org_qhub_analytics_config = organization.config.get('qhub_analytics')

                if org_qhub_analytics_config:
                    video_data['qhub_analytics_enabled'] = org_qhub_analytics_config.get('enabled',
                                                                                         '')
                    video_data['qhub_analytics_plugin_url'] = org_qhub_analytics_config.get(
                        'plugin_url', '')

                context.update(video_data)
        else:
            context['error'] = True
            context['message'] = 'Content is not available on this site.'

        return context

    @staticmethod
    def get_video_data(video_id):
        live_video = LiveVideo.objects.filter(video_id=video_id).first()

        if live_video:
            video_url = f'https://{live_video.cf_domain}/output.m3u8'
            poster_url = ''
            mime_type = 'application/x-mpegURL'

            return poster_url, live_video, video_url, mime_type

        media = Media.objects.filter(video_id=video_id).first()

        if media:
            poster_url, media_url, mime_type = media.get_urls()

            return poster_url, media, media_url, mime_type

        raise Http404('Video not found')
