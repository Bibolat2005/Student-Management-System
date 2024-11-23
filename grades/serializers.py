from django.forms import ValidationError
from rest_framework import serializers
from .models import Grade
from students.models import Student
from courses.models import Course
from users.models import CustomUser

class GradeSerializer(serializers.ModelSerializer):
    """
    Serializer for grade records, containing information on the grade value, date,
    course, and student.
    """
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(is_teacher=True))
    grade_value = serializers.FloatField(required=True, write_only=True)
    created_at = serializers.DateTimeField(read_only=True, default_timezone='UTC')


    class Meta:
        model = Grade
        fields = '__all__'

    class Meta:
        model = Grade
        fields = '__all__'

    def validate_student(self, value):
        """
        Проверка, что студент действительно существует и может получить оценку.
        """
        if not Student.objects.filter(user=value.user).exists():
            raise ValidationError("This student does not exist.")
        return value

    def validate_course(self, value):
        """
        Проверка, что курс существует.
        """
        if not Course.objects.filter(name=value.name).exists():
            raise ValidationError("This course does not exist.")
        return value

    def validate_teacher(self, value):
        """
        Проверка, что преподаватель является активным преподавателем.
        """
        if not CustomUser.objects.filter(email=value.email, is_teacher=True).exists():
            raise ValidationError("This user is not a valid teacher.")
        return value

    def create(self, validated_data):
        """
        Переопределенный метод create для дополнительной логики перед сохранением.
        Здесь можно добавить дополнительные изменения или логику.
        """
        grade_value = validated_data.pop('grade_value')
        created_at = validated_data.pop('created_at', None) 
        grade_instance = Grade.objects.create(grade_value=grade_value, **validated_data)
        return grade_instance
