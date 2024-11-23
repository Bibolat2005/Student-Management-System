from django.urls import path
from .views import  PopularCoursesView
urlpatterns = [
    # path('most-active-users/', MostActiveUsersView.as_view(), name='most_active_users'),
    path('popular-courses/', PopularCoursesView.as_view(), name='popular_courses'),
    # path('stats/', ThrottlingStats.as_view(), name='throttling-stats'),
]