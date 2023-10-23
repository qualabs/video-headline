from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

from player.views import EmbedView

from organization.models import Organization, Channel
from test_utils import create_organizations, create_user, create_channels, create_videos, \
    add_channel_to_video, create_live_videos
from video.models import Media, LiveVideo

INVALID_DOMAIN_MESSAGE = 'Content is not available on this site.'
UNAVAILABLE_MESSAGE = 'The content is not available.'


class PlayerTests(TestCase):

    @classmethod
    def setUpClass(cls):
        # Organizations
        cls.org1 = create_organizations('Organization', 1)[0]

        # Users
        cls.user1 = create_user('user1', '12345678', cls.org1)

    def setUp(self):
        # Channel with ads_vast_url
        self.chan1 = \
            create_channels('Channel with ads vast', self.org1, 1, [],
                            'http://www.channel-vast-url.com')[0]

        # Channel with autoplay
        self.chan2 = \
            create_channels('Channel with autoplay', self.org1, 1, [], None, False, True)[0]

        # Channel with allowed domains
        self.chan3 = \
            create_channels('Channel with all allowed domains', self.org1, 1, [])[0]

        self.chan4 = \
            create_channels('Channel with simple allowed domain', self.org1, 1,
                            ['www.allowed-domain.com'])[0]

        self.chan5 = \
            create_channels('Channel with wildcard domain', self.org1, 1, ['www.*.test.com'])[0]

        self.chan6 = \
            create_channels('Channel with double wildcard domain', self.org1, 1,
                            ['www.*.*.test.com'])[0]

        self.chan7 = \
            create_channels('Channel with common domain', self.org1, 1, ['*.domain.com'])[0]

        # Video with default options
        self.video1 = \
            create_videos('Video', self.user1, self.org1, 1, Media.State.FINISHED)[0]
        add_channel_to_video(self.chan1, self.video1)

        # Video with ads_vast_url and without enabled ads
        self.video2 = \
            create_videos('Video with ads vast and without enable ads', self.user1, self.org1, 1,
                          Media.State.FINISHED, None, 'http://www.video-vast-url.com', False)[0]
        add_channel_to_video(self.chan1, self.video2)

        # Video with ads_vast_url
        self.video3 = \
            create_videos('Video with ads vast', self.user1, self.org1, 1, Media.State.FINISHED,
                          None, 'http://www.video-vast-url.com')[0]
        add_channel_to_video(self.chan1, self.video3)

        # Video without ads_vast_url and with enable_ads false
        self.video4 = \
            create_videos('Video without ads vast and with enable ads', self.user1, self.org1, 1,
                          Media.State.FINISHED, None,
                          None, False)[0]
        add_channel_to_video(self.chan1, self.video4)

        # Videos with autoplay options
        self.video5 = \
            create_videos('Video with autoplay no', self.user1, self.org1, 1, Media.State.FINISHED,
                          None, None, True, 'n')[0]
        add_channel_to_video(self.chan1, self.video5)

        self.video6 = \
            create_videos('Video with autoplay yes', self.user1, self.org1, 1,
                          Media.State.FINISHED, None, None, True, 'y')[0]
        add_channel_to_video(self.chan1, self.video6)

        self.client = Client(HTTP_REFERER='http://qhub-tests.com')


    def tearDown(self):
        Media.objects.all().delete()
        Channel.objects.all().delete()

    @classmethod
    def tearDownClass(cls):
        cls.org1.delete()

    # <editor-fold desc="Video vast TESTS">
    def test_video_override_channel_vast(self):
        url = reverse('embed', kwargs={'channel_id': self.chan1.channel_id,
                                       'video_id': self.video3.video_id})
        response = self.client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate adTagUrl in response
        self.assertEquals(self.video3.ads_vast_url, response.context['adTagUrl'])

    def test_video_without_vast(self):
        url = reverse('embed', kwargs={'channel_id': self.chan1.channel_id,
                                       'video_id': self.video1.video_id})
        response = self.client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate adTagUrl in response
        self.assertEquals(self.chan1.ads_vast_url, response.context['adTagUrl'])

    # </editor-fold>

    # <editor-fold desc="Video no-ads flag TESTS">
    def test_video_flag_override_channel_vast(self):
        url = reverse('embed', kwargs={'channel_id': self.chan1.channel_id,
                                       'video_id': self.video3.video_id})
        response = self.client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate adTagUrl in response
        self.assertEquals(self.video3.ads_vast_url, response.context['adTagUrl'])

    def test_video_flag_use_channel_vast(self):
        url = reverse('embed', kwargs={'channel_id': self.chan1.channel_id,
                                       'video_id': self.video1.video_id})
        response = self.client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate adTagUrl in response
        self.assertEquals(self.chan1.ads_vast_url, response.context['adTagUrl'])

    def test_video_flag_false_vast(self):
        url = reverse('embed', kwargs={'channel_id': self.chan1.channel_id,
                                       'video_id': self.video4.video_id})
        response = self.client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate adTagUrl in response
        self.assertEquals('', response.context['adTagUrl'])

    def test_video_flag_false_without_vast(self):
        url = reverse('embed', kwargs={'channel_id': self.chan1.channel_id,
                                       'video_id': self.video4.video_id})
        response = self.client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate adTagUrl in response
        self.assertEquals('', response.context['adTagUrl'])

    # </editor-fold>

    # <editor-fold desc="Allowed Domain TESTS">
    def test_valid_all_domains(self):
        client = Client(HTTP_REFERER='http://www.allowed-domain.com')
        add_channel_to_video(self.chan3, self.video3)

        url = reverse('embed',
                      kwargs={'video_id': self.video3.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertFalse(response.context['error'])

    def test_valid_simple_domain(self):
        client = Client(HTTP_REFERER='http://www.allowed-domain.com')
        add_channel_to_video(self.chan4, self.video3)

        url = reverse('embed',
                      kwargs={'video_id': self.video3.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertFalse(response.context['error'])

    def test_invalid_simple_domain(self):
        client = Client(HTTP_REFERER='http://www.not-allowed-domain.com')
        add_channel_to_video(self.chan4, self.video3)

        url = reverse('embed',
                      kwargs={'video_id': self.video3.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertTrue(response.context['error'])

        # Validate specific error message
        self.assertEqual(INVALID_DOMAIN_MESSAGE, response.context['message'])

    # VALID WILDCARD
    def test_valid_wildcard_domain(self):
        client = Client(HTTP_REFERER='http://www.wildcard.test.com')
        add_channel_to_video(self.chan5, self.video3)

        url = reverse('embed', kwargs={'video_id': self.video3.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertFalse(response.context['error'])

    def test_second_valid_wildcard_domain(self):
        client = Client(HTTP_REFERER='http://www.wild-card.test.com')
        add_channel_to_video(self.chan5, self.video3)

        url = reverse('embed', kwargs={'video_id': self.video3.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertFalse(response.context['error'])

    def test_third_valid_wildcard_domain(self):
        client = Client(HTTP_REFERER='http://www.wild_c4rd-test.test.com')
        add_channel_to_video(self.chan5, self.video3)

        url = reverse('embed', kwargs={'video_id': self.video3.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertFalse(response.context['error'])

    def test_valid_double_wildcard_domain(self):
        client = Client(HTTP_REFERER='http://www.wild.card.test.com')
        add_channel_to_video(self.chan6, self.video3)

        url = reverse('embed', kwargs={'video_id': self.video3.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertFalse(response.context['error'])

    def test_valid_common_domain(self):
        client = Client(HTTP_REFERER='http://www.domain.com')
        add_channel_to_video(self.chan7, self.video3)

        url = reverse('embed', kwargs={'video_id': self.video3.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertFalse(response.context['error'])

    # INVALID WILDCARD
    def test_invalid_wildcard_domain(self):
        client = Client(HTTP_REFERER='http://www.wildcard.test.invalid.com')
        add_channel_to_video(self.chan5, self.video3)

        url = reverse('embed', kwargs={'video_id': self.video3.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertTrue(response.context['error'])

        # Validate specific error message
        self.assertEqual(INVALID_DOMAIN_MESSAGE, response.context['message'])

    def test_second_invalid_wildcard_domain(self):
        client = Client(HTTP_REFERER='http://www.test.com')
        add_channel_to_video(self.chan5, self.video3)

        url = reverse('embed', kwargs={'video_id': self.video3.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertTrue(response.context['error'])

        # Validate specific error message
        self.assertEqual(INVALID_DOMAIN_MESSAGE, response.context['message'])

    def test_third_invalid_wildcard_domain(self):
        client = Client(HTTP_REFERER='http://www.invalid.wildcard.test.com')
        add_channel_to_video(self.chan5, self.video3)

        url = reverse('embed', kwargs={'video_id': self.video3.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertTrue(response.context['error'])

        # Validate specific error message
        self.assertEqual(INVALID_DOMAIN_MESSAGE, response.context['message'])

    def test_fourth_invalid_wildcard_domain(self):
        client = Client(HTTP_REFERER='http://www..test.com')
        add_channel_to_video(self.chan5, self.video3)

        url = reverse('embed', kwargs={'video_id': self.video3.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertTrue(response.context['error'])

        # Validate specific error message
        self.assertEqual(INVALID_DOMAIN_MESSAGE, response.context['message'])

    def test_invalid_double_wildcard_domain(self):
        client = Client(HTTP_REFERER='http://www.wild.test.com')
        add_channel_to_video(self.chan6, self.video3)

        url = reverse('embed', kwargs={'video_id': self.video3.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertTrue(response.context['error'])

        # Validate specific error message
        self.assertEqual(INVALID_DOMAIN_MESSAGE, response.context['message'])

    def test_second_invalid_double_wildcard_domain(self):
        client = Client(HTTP_REFERER='http://www.wild.test.card.com')
        add_channel_to_video(self.chan6, self.video3)

        url = reverse('embed', kwargs={'video_id': self.video3.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertTrue(response.context['error'])

        # Validate specific error message
        self.assertEqual(INVALID_DOMAIN_MESSAGE, response.context['message'])

    # VIDEO AUTOPLAY
    def test_channel_autoplay_with_video_autoplay_channel_must_autoplay(self):
        """
        The channel as autoplay, the video has autoplay as the channel config.
        The video must autoplay
        """
        client = Client()
        add_channel_to_video(self.chan2, self.video1)
        url = reverse('embed', kwargs={'channel_id': self.chan2.channel_id,
                                       'video_id': self.video1.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # We check against the string given that it must be the word 'True' for it to work
        # and not something that evaluates to True
        self.assertTrue(str(response.context['autoplay']) == 'True')

    def test_channel_autoplay_with_video_autoplay_no_must_not_autoplay(self):
        """
        The channel as autoplay, the video has autoplay as no.
        The video must not autoplay
        """
        client = Client()
        add_channel_to_video(self.chan2, self.video5)
        url = reverse('embed', kwargs={'channel_id': self.chan2.channel_id,
                                       'video_id': self.video5.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate autoplay in response
        self.assertTrue(response.context['autoplay'] == '')

    def test_channel_autoplay_with_video_autoplay_yes_must_autoplay(self):
        """
        The channel as autoplay, the video has autoplay activated.
        The video must not autoplay
        """
        client = Client()
        add_channel_to_video(self.chan2, self.video6)
        url = reverse('embed', kwargs={'channel_id': self.chan2.channel_id,
                                       'video_id': self.video6.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # We check against the string given that it must be the word 'True' for it to work
        # and not something that evaluates to True
        self.assertTrue(str(response.context['autoplay']) == 'True')

    def test_channel_no_autoplay_with_video_autoplay_channel_must_not_autoplay(self):
        """
        The channel has no autoplay, the video has autoplay as channel.
        The video must not autoplay
        """
        client = Client()
        url = reverse('embed', kwargs={'channel_id': self.chan1.channel_id,
                                       'video_id':
                                           self.video1.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate autoplay in response
        self.assertTrue(response.context['autoplay'] == '')

    def test_channel_no_autoplay_with_video_autoplay_no_must_not_autoplay(self):
        """
        The channel has no autoplay, the video has autoplay no autoplay.
        The video must not autoplay
        """
        client = Client()
        url = reverse('embed', kwargs={'channel_id': self.chan1.channel_id,
                                       'video_id':
                                           self.video5.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate autoplay in response
        self.assertTrue(response.context['autoplay'] == '')

    def test_channel_no_autoplay_with_video_autoplay_yes_must_autoplay(self):
        """
        The channel has no autoplay, the video has autoplay activated.
        The video must autoplay
        """
        client = Client()
        url = reverse('embed', kwargs={'channel_id': self.chan1.channel_id,
                                       'video_id':
                                           self.video6.video_id})
        response = client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # We check against the string given that it must be the word 'True' for it to work
        # and not something that evaluates to True
        self.assertTrue(str(response.context['autoplay']) == 'True')

    # </editor-fold>

    # <editor-fold desc="Available Content Test"
    def test_error_message_video_state_waiting_file(self):
        video = \
            create_videos('Video', self.user1, self.org1, 1, Media.State.WAITING_FILE, None, None,
                          False)[0]
        add_channel_to_video(self.chan1, video)

        url = reverse('embed',
                      kwargs={'channel_id': self.chan1.channel_id,
                              'video_id': video.video_id})
        response = self.client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertTrue(response.context['error'])

        # Validate specific error message
        self.assertEqual(UNAVAILABLE_MESSAGE, response.context['message'])

    def test_error_message_video_state_queued(self):
        video = \
            create_videos('Video', self.user1, self.org1, 1, Media.State.QUEUED, None, None,
                          False)[0]
        add_channel_to_video(self.chan1, video)

        url = reverse('embed',
                      kwargs={'channel_id': self.chan1.channel_id,
                              'video_id': video.video_id})
        response = self.client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertTrue(response.context['error'])

        # Validate specific error message
        self.assertEqual(UNAVAILABLE_MESSAGE, response.context['message'])

    def test_error_message_video_state_queued_failed(self):
        video = \
            create_videos('Video', self.user1, self.org1, 1, Media.State.QUEUING_FAILED, None,
                          None, False)[0]
        add_channel_to_video(self.chan1, video)

        url = reverse('embed',
                      kwargs={'channel_id': self.chan1.channel_id,
                              'video_id': video.video_id})
        response = self.client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertTrue(response.context['error'])

        # Validate specific error message
        self.assertEqual(UNAVAILABLE_MESSAGE, response.context['message'])

    def test_error_message_video_state_processing(self):
        video = \
            create_videos('Video', self.user1, self.org1, 1, Media.State.PROCESSING, None,
                          None, False)[0]
        add_channel_to_video(self.chan1, video)

        url = reverse('embed',
                      kwargs={'channel_id': self.chan1.channel_id,
                              'video_id': video.video_id})
        response = self.client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertTrue(response.context['error'])

        # Validate specific error message
        self.assertEqual(UNAVAILABLE_MESSAGE, response.context['message'])

    def test_error_message_video_state_processing_failed(self):
        video = \
            create_videos('Video', self.user1, self.org1, 1, Media.State.PROCESSING_FAILED, None,
                          None, False)[0]
        add_channel_to_video(self.chan1, video)

        url = reverse('embed',
                      kwargs={'channel_id': self.chan1.channel_id,
                              'video_id': video.video_id})
        response = self.client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertTrue(response.context['error'])

        # Validate specific error message
        self.assertEqual(UNAVAILABLE_MESSAGE, response.context['message'])

    def test_error_message_video_state_not_finished(self):
        video = \
            create_videos('Video', self.user1, self.org1, 1, Media.State.NOT_FINISHED, None,
                          None, False)[0]
        add_channel_to_video(self.chan1, video)

        url = reverse('embed',
                      kwargs={'channel_id': self.chan1.channel_id,
                              'video_id': video.video_id})
        response = self.client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertTrue(response.context['error'])

        # Validate specific error message
        self.assertEqual(UNAVAILABLE_MESSAGE, response.context['message'])

    def test_error_message_video_state_failed(self):
        video = \
            create_videos('Video', self.user1, self.org1, 1, Media.State.FAILED, None,
                          None, False)[0]
        add_channel_to_video(self.chan1, video)

        url = reverse('embed',
                      kwargs={'channel_id': self.chan1.channel_id,
                              'video_id': video.video_id})
        response = self.client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertTrue(response.context['error'])

        # Validate specific error message
        self.assertEqual(UNAVAILABLE_MESSAGE, response.context['message'])

    def test_error_message_video_with_disabled_org(self):
        video = \
            create_videos('Video', self.user1, self.org1, 1, Media.State.FAILED, None,
                          None, False)[0]
        add_channel_to_video(self.chan1, video)

        self.org1.upload_enable = False
        self.org1.save()

        url = reverse('embed',
                      kwargs={'channel_id': self.chan1.channel_id,
                              'video_id': video.video_id})
        response = self.client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertTrue(response.context['error'])

        # Validate specific error message
        self.assertEqual(UNAVAILABLE_MESSAGE, response.context['message'])

        self.org1.upload_enable = True
        self.org1.save()

    def test_error_message_live_video_state_starting(self):
        live = \
            create_live_videos('Live', self.user1, self.org1, 1, LiveVideo.State.STARTING, None,
                               None, False)[0]
        add_channel_to_video(self.chan1, live)

        url = reverse('embed',
                      kwargs={'channel_id': self.chan1.channel_id,
                              'video_id': live.video_id})
        response = self.client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertTrue(response.context['error'])

        # Validate specific error message
        self.assertEqual(UNAVAILABLE_MESSAGE, response.context['message'])

    def test_error_message_live_video_state_stopping(self):
        live = \
            create_live_videos('Live', self.user1, self.org1, 1, LiveVideo.State.STOPPING, None,
                               None, False)[0]
        add_channel_to_video(self.chan1, live)

        url = reverse('embed',
                      kwargs={'channel_id': self.chan1.channel_id,
                              'video_id': live.video_id})
        response = self.client.get(url)

        # Validate error in response
        self.assertTrue(response.context['error'])

        # Validate specific error message
        self.assertEqual(UNAVAILABLE_MESSAGE, response.context['message'])

    def test_error_message_live_video_state_off(self):
        live = \
            create_live_videos('Live', self.user1, self.org1, 1, LiveVideo.State.OFF, None,
                               None, False)[0]
        add_channel_to_video(self.chan1, live)

        url = reverse('embed',
                      kwargs={'channel_id': self.chan1.channel_id,
                              'video_id': live.video_id})
        response = self.client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertTrue(response.context['error'])

        # Validate specific error message
        self.assertEqual(UNAVAILABLE_MESSAGE, response.context['message'])


    def test_no_error_message_live_video_state_on(self):
        live = \
            create_live_videos('Live', self.user1, self.org1, 1, LiveVideo.State.ON, None,
                               None, False)[0]
        add_channel_to_video(self.chan1, live)

        url = reverse('embed',
                      kwargs={'channel_id': self.chan1.channel_id,
                              'video_id': live.video_id})
        response = self.client.get(url)

        # Validate status code
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # Validate error in response
        self.assertFalse(response.context['error'])

    # </editor-fold>

    def test_audio_creation_url(self):
         # Audio with default options
        self.audio = \
            create_videos('Audio default', self.user1, self.org1, 1, Media.State.FINISHED, media_type='audio')[0]
        add_channel_to_video(self.chan1, self.audio)

        url = reverse('embed',
                      kwargs={'channel_id': self.chan1.channel_id,
                              'video_id': self.audio.video_id})
        
        response = self.client.get(url)

        type = response.context['type']
        self.assertEquals(type, 'audio/mp4')

        url = response.context['url']
        self.assertTrue('audio/output.mp4' in url)
        
    def test_video_creation_url(self):
         # Video with default options
        self.video = \
            create_videos('Video default', self.user1, self.org1, 1, Media.State.FINISHED, media_type='video')[0]
        add_channel_to_video(self.chan1, self.video)

        url = reverse('embed',
                      kwargs={'channel_id': self.chan1.channel_id,
                              'video_id': self.video.video_id})
        
        response = self.client.get(url)

        type = response.context['type']
        self.assertEquals(type, 'application/x-mpegURL')

        url = response.context['url']
        self.assertTrue('hls/output.m3u8' in url)
