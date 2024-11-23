from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CourseView
from django.shortcuts import render
from .models import ActiveUser, CourseView
from analytics import models

class PopularCoursesView(APIView):
    def get(self, request, *args, **kwargs):
        # Get most viewed courses
        popular_courses = CourseView.objects.values('course').annotate(view_count=models.Count('course')).order_by('-view_count')[:5]
        return Response(popular_courses)



def dashboard(request):
    active_users = ActiveUser.objects.all().order_by('-request_count')[:10]
    popular_courses = CourseView.objects.values('course').annotate(view_count=models.Count('course')).order_by('-view_count')[:5]
    
    context = {
        'active_users': active_users,
        'popular_courses': popular_courses
    }
    return render(request, 'analytics/dashboard.html', context)