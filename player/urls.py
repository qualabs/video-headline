from django.urls import path

from player.views import EmbedView

urlpatterns = [
    path('embed/<str:video_id>/', EmbedView.as_view(), name='embed'),
    path('embed/<str:channel_id>/<str:video_id>/', EmbedView.as_view(), name='embed'),
]
