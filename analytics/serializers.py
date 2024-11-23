from rest_framework import serializers
from .models import MostActiveUser, PopularCourse

class MostActiveUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MostActiveUser
        fields = ['user', 'request_count']

class PopularCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PopularCourse
        fields = ['course', 'access_count']