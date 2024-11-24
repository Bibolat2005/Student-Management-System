from django.db import models
from django.contrib.auth import get_user_model
from courses.models import Course

User = get_user_model()

class APIRequestLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.endpoint} ({self.method})"

class MostActiveUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    request_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.request_count} requests"

class PopularCourse(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE)
    access_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.course.name} - {self.access_count} views"

class ThrottlingMetrics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='throttling_metrics')
    daily_request_count = models.IntegerField(default=0)
    last_request_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.daily_request_count} requests"