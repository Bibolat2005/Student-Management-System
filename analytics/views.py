from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import MostActiveUser, PopularCourse
from .serializers import MostActiveUserSerializer, PopularCourseSerializer
from analytics.models import ThrottlingMetrics

class MostActiveUsersView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        active_users = MostActiveUser.objects.order_by('-request_count')[:10]
        serializer = MostActiveUserSerializer(active_users, many=True)
        return Response(serializer.data)

class PopularCoursesView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        popular_courses = PopularCourse.objects.order_by('-access_count')[:10]
        serializer = PopularCourseSerializer(popular_courses, many=True)
        return Response(serializer.data)



class ThrottlingStats(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = ThrottlingMetrics.objects.all().values(
            'user__username', 'daily_request_count', 'last_request_time'
        )
        return Response(list(data))
    


from django.shortcuts import render
from .models import MostActiveUser, PopularCourse

def dashboard(request):
    active_users = MostActiveUser.objects.order_by('-request_count')[:10]
    
    popular_courses = PopularCourse.objects.order_by('-access_count')[:5]
    
    context = {
        'active_users': active_users,
        'popular_courses': popular_courses
    }
    return render(request, 'analytics/dashboard.html', context)
