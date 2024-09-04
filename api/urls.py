from rest_framework.routers import DefaultRouter
from .views import UserViewSet, StatusUpdateViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'status-updates', StatusUpdateViewSet, basename='statusupdate')

urlpatterns = router.urls
