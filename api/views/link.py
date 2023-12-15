from base64 import b64encode
import json

import datetime

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from botocore.signers import CloudFrontSigner
from django.conf import settings
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

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
        video = Media.objects.filter(video_id=video_id, organization=organization).first()

        if video:
            org = video.organization
            if org.security_enabled:
                # CloudFront distribution URL
                cf_url = video.channel.cf_domain

                resource_path = f'https://{cf_url}/{video_id}/hls/output.m3u8'

                # Expiry date for the signed URL
                expire_date = datetime.datetime(2024, 1, 1)

                # Create a CloudFrontSigner instance with the key group ID
                cloudfront_signer = CloudFrontSigner(org.public_key_id, rsa_signer)

                policy = {
                    "Statement": [
                        {
                            "Resource": resource_path,
                            "Condition": {
                                "DateLessThan": {
                                    "AWS:EpochTime": int(expire_date.timestamp())
                                }
                            }
                        }
                    ]
                }

                policy_json_str = json.dumps(policy)

                # Create a signed URL that will be valid until the specified expiry date
                signed_url = cloudfront_signer.generate_presigned_url(resource_path, policy=policy_json_str)
                print(signed_url)

                base_url, query_params = signed_url.split('?')

                embed_url = f'{settings.BASE_URL}player/embed/{video_id}/hls/*?{query_params}'
                response = {
                    'embed_url': embed_url,
                    'embed_code': f"<iframe src='{embed_url}' width='560' height='315' frameBorder='0' scrolling='no' seamless='seamless' allow='autoplay;fullscreen'> </iframe>",
                }
            else:
                _, video_url, mime_type = video.get_urls()
                response = {
                    'video_url': video_url,
                    'type': mime_type
                }
            return response

        else:
            return None

    @staticmethod
    def get_live_video(video_id, organization):
        live = LiveVideo.objects.filter(video_id=video_id, organization=organization).first()
        if live:
            org = live.organization
            if org.security_enabled:
                token = get_base64_token(f'https://{live.cf_domain}/*',
                                         org.aws_account.cf_private_key,
                                         org.aws_account.cf_public_key)
                embed_url = f'{settings.BASE_URL}player/embed/{video_id}/?token={token}'
                response = {
                    'embed_url': embed_url,
                    'embed_code': f"<iframe src='{embed_url}' width='560' height='315' frameBorder='0' scrolling='no' seamless='seamless' allow='autoplay;fullscreen'> </iframe>",
                    'token': token
                }
            else:
                response = {
                    'video_url': f'https://{live.cf_domain}/output.m3u8',
                    'type': 'application/x-mpegURL'
                }
            return response

        else:
            return None


def rsa_signer(message):
    with open('private_key.pem', 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())
