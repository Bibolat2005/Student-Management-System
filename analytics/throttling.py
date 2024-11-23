from rest_framework.throttling import UserRateThrottle

class CustomUserThrottle(UserRateThrottle):
    scope = 'custom_user'

    def allow_request(self, request, view):
        user = request.user
        if user.is_authenticated:
            from analytics.models import ThrottlingMetrics
            throttling, _ = ThrottlingMetrics.objects.get_or_create(user=user)
            throttling.request_count += 1
            throttling.save()
        return super().allow_request(request, view)