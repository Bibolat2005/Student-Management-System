from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')

urlpatterns = [
    path('api/users/auth/jwt/create/', TokenObtainPairView.as_view(), name='token_create'),
    path('api/users/auth/jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # другие пути, если есть
]

urlpatterns = router.urls
