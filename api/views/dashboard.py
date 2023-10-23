from rest_framework.response import Response
from rest_framework.views import APIView

from video.models import LiveVideo, Media


class DashboardView(APIView):
    """
    Returns data related to videos to display on the Website Dashboard
    """

    def _get_videos(self):
        organization = self.request.user.organization_id

        return Media.objects.filter(organization_id=organization)

    def _get_live_videos(self):
        organization = self.request.user.organization_id

        return LiveVideo.objects.filter(organization_id=organization)

    def get(self, request, format=None):
        user = self.request.user

        response = {
            'videos_in_process': self._get_videos().filter(state=Media.State.PROCESSING).count(),
            'failed_videos': self._get_videos().filter(
                state__in=[Media.State.QUEUING_FAILED, Media.State.PROCESSING_FAILED]).count(),
            'uploaded_by_user': self._get_videos().filter(created_by=user).count(),
            'uploaded_by_org': self._get_videos().count(),
            'live_videos_by_org': self._get_live_videos().count()
        }

        return Response(response)
