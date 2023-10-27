from base64 import b64encode

import uuid

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from urllib.parse import quote

from video.models import Media, LiveVideo


class VideoLink(APIView):
    def get(self, request, video_id):
        organization = request.user.organization.pk

        response = self.get_video(video_id, organization)
        if response is not None:
            return Response(response)

        response = self.get_live_video(video_id, organization)
        if response is not None:
            return Response(response)

        raise NotFound()

    @staticmethod
    def get_video(video_id, organization):
        video = Media.objects.filter(
            video_id=video_id, organization=organization
        ).first()

        if video:
            org = video.organization
            if org.security_enabled:
                resource = f'https://{video.channel.cf_domain}/{video_id}/*'
                token = get_base64_token(
                    resource,
                    org.aws_account.cf_private_key,
                    org.aws_account.cf_key_pair_id,
                )
                embed_url = (
                                f"{settings.BASE_URL}player/embed/{video_id}/"
                                f"?token={token}"
                            )
                response = {
                    'embed_url': embed_url,
                    'embed_code': (
                                    f"<iframe src='{embed_url}' width='560'"
                                    f"height='315' frameBorder='0'"
                                    f"scrolling='no' eamless='seamless' "
                                    f"allow='autoplay;fullscreen'> </iframe>"
                                ),
                    'token': token,
                }
            else:
                _, video_url, mime_type = video.get_urls()
                response = {'video_url': video_url, 'type': mime_type}
            return response

        else:
            return None

    @staticmethod
    def get_live_video(video_id, organization):
        live = LiveVideo.objects.filter(
            video_id=video_id, organization=organization
        ).first()
        if live:
            org = live.organization
            if org.security_enabled:
                token = get_base64_token(
                    f'https://{live.cf_domain}/*',
                    org.aws_account.cf_private_key,
                    org.aws_account.cf_key_pair_id,
                )
                embed_url = (
                    f"{settings.BASE_URL}player/embed/{video_id}/"
                    f"?token={token}"
                )
                response = {
                    'embed_url': embed_url,
                    'embed_code': (
                                    f"<iframe src='{embed_url}' width='560'"
                                    f"height='315' frameBorder='0' "
                                    f"scrolling='no' "
                                    f"seamless='seamless' "
                                    f"allow='autoplay;fullscreen'> "
                                    f"</iframe>"
                                ),
                    'token': token,
                }
            else:
                response = {
                    'video_url': f'https://{live.cf_domain}/output.m3u8',
                    'type': 'application/x-mpegURL',
                }
            return response

        else:
            return None


def get_base64_token(resource, priv_key, key_pair_id):
    date = (timezone.now() + timedelta(hours=12)).strftime('%s')
    policy = (
        '{"Statement":[{"Resource":"'
        + resource
        + '","Condition":{"DateLessThan":{"AWS:EpochTime":'
        + date
        + '}},"id":"'
        + str(uuid.uuid4())
        + '"}]}'
    ).encode('utf-8')

    policy_b64 = quote(b64encode(policy))
    pk = serialization.load_pem_private_key(
        priv_key.encode('utf8'), password=None, backend=default_backend()
    )
    signature = pk.sign(policy, padding.PKCS1v15(), hashes.SHA1())
    signature_b64 = quote(b64encode(signature))
    token = (
        f"?Policy={policy_b64}&Signature={signature_b64}"
        f"&Key-Pair-Id={key_pair_id}"
    )
    return b64encode(token.encode('utf-8')).decode('utf-8')
