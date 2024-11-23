from django.db import models
from django.contrib.auth.models import User
from courses.models import Course
from django.conf import settings
# Model to track the number of API requests per user
class UserRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    endpoint = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.user.email} - {self.endpoint} - {self.timestamp}"

# Model to track the number of views for each course
class CourseView(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"User {self.user.email} viewed course {self.course.name} on {self.timestamp}"

# Model to track most active users based on API requests
class ActiveUser(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    request_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.email} - {self.request_count} requests"
