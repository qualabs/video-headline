from django.urls import path, include
from knox import views as knox_views
from rest_framework.routers import SimpleRouter
from rest_framework_swagger.views import get_swagger_view

from api.views import AccountViewSet, LoginView, MediaViewSet, TagViewSet, OrganizationViewSet, \
    ChannelViewSet, DashboardView, LiveVideoViewSet, status, LiveVideoCutsViewSet, VideoLink, \
    BillsViewSet

router = SimpleRouter()

router.register(r'accounts', AccountViewSet, base_name='accounts')
router.register(r'videos', MediaViewSet, base_name='videos')
router.register(r'media', MediaViewSet, base_name='media')
router.register(r'tags', TagViewSet, base_name='tags')
router.register(r'organizations', OrganizationViewSet, base_name='organizations')
router.register(r'channels', ChannelViewSet, base_name='channels')
router.register(r'live-videos', LiveVideoViewSet, base_name='live-videos')
router.register(r'cuts', LiveVideoCutsViewSet, base_name='cuts')
router.register(r'bills', BillsViewSet, base_name='bills')

schema_view = get_swagger_view(title='VideoHeadline API')

urlpatterns = [
    path('', include(router.urls)),
    path('status/', status, name='status'),
    path('link/<str:video_id>/', VideoLink.as_view(), name='link'),
    path('swagger/', schema_view),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('token/login/', LoginView.as_view(), name='knox_login'),
    path('token/logout/', knox_views.LogoutView.as_view(), name='knox_login'),
    path('token/logoutall/', knox_views.LogoutAllView.as_view(), name='knox_login'),
]
