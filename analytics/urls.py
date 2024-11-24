from django.urls import path
from .views import MostActiveUsersView, PopularCoursesView, ThrottlingStats
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('most-active-users/', MostActiveUsersView.as_view(), name='most_active_users'),
    path('popular-courses/', PopularCoursesView.as_view(), name='popular_courses'),
    path('stats/', ThrottlingStats.as_view(), name='throttling-stats'),
    path('api/users/auth/jwt/create/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/users/auth/jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
