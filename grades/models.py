from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from StudentManagementSystem import settings
from students.models import Student
from courses.models import Course
from users.models import CustomUser

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades')
    grade = models.CharField(max_length=2)
    date = models.DateField(auto_now_add=True)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='grades_given'
    )
    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} got {self.grade} in {self.course}"



