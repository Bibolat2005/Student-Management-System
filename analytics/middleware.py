import logging
from datetime import datetime
from courses.models import Course
from analytics.models import APIRequestLog, MostActiveUser, PopularCourse
from django.utils.timezone import now
from analytics.models import ThrottlingMetrics
from django.core.cache import cache

logger = logging.getLogger(__name__)

class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            APIRequestLog.objects.create(
                user=request.user,
                endpoint=request.path,
                method=request.method,
                status_code=response.status_code,
                timestamp=datetime.now()
            )
            active_user, _ = MostActiveUser.objects.get_or_create(user=request.user)
            active_user.request_count += 1
            active_user.save()

        if 'courses' in request.path:
            course_id = request.GET.get('course_id')
            if course_id:
                try:
                    course = Course.objects.get(id=course_id)
                    popular_course, _ = PopularCourse.objects.get_or_create(course=course)
                    popular_course.access_count += 1
                    popular_course.save()
                except Course.DoesNotExist:
                    logger.error(f"Course with ID {course_id} does not exist.")

        return response





class ThrottlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            throttling, created = ThrottlingMetrics.objects.get_or_create(user=request.user)
            if throttling.last_request_time and throttling.last_request_time.date() < now().date():
                throttling.daily_request_count = 0

            throttling.daily_request_count += 1
            throttling.last_request_time = now()
            throttling.save()


        if request.user.is_authenticated:
            cache_key = f"user_{request.user.id}_daily_requests"
            daily_requests = cache.get(cache_key, 0)
            cache.set(cache_key, daily_requests + 1, timeout=86400)  
            response = self.get_response(request)
            return response
        response = self.get_response(request)
        return response