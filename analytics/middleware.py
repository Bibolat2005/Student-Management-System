from .models import UserRequest
from django.utils.timezone import now

class TrackAPIRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Track request if the user is authenticated
        if request.user.is_authenticated:
            UserRequest.objects.create(
                user=request.user,
                endpoint=request.path,
                timestamp=now()
            )
        response = self.get_response(request)
        return response
