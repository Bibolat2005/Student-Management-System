from django.urls import include, path
from rest_framework.routers import DefaultRouter
from students.views import StudentViewSet


router = DefaultRouter()
router.register(r'profiles', StudentViewSet, basename='student-profile')

urlpatterns = [
    path('api/students/', include(router.urls)),
]
urlpatterns = router.urls