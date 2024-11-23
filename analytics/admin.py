from django.contrib import admin
from .models import UserRequest, CourseView, ActiveUser

admin.site.register(UserRequest)
admin.site.register(CourseView)
admin.site.register(ActiveUser)