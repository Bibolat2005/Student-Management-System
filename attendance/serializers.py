from rest_framework import serializers
from .models import Attendance
from students.serializers import StudentSerializer
from courses.serializers import CourseSerializer
from students.models import Student
from courses.models import Course

class AttendanceSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

    class Meta:
        model = Attendance
        fields = '__all__'

    def get_status(self, obj):
        return 'Present' if obj.present else 'Absent'