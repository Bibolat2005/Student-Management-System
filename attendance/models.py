from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from students.models import Student
from courses.models import Course

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=False)
    status = models.CharField(max_length=20, choices=[('present', 'Present'), ('absent', 'Absent')])
    class Meta:
        unique_together = ('student', 'course', 'date')


    def __str__(self):
        return f"{self.student} - {self.course} - {'Present' if self.present else 'Absent'}"


def invalidate_attendance_cache(instance):
    cache.delete('attendance_list')
    cache_key = f'attendance_detail_{instance.pk}'
    cache.delete(cache_key)


@receiver(post_save, sender=Attendance)
def attendance_saved_handler(sender, instance, **kwargs):
    """Очищает кеш после сохранения записи о посещаемости."""
    invalidate_attendance_cache(instance)


@receiver(post_delete, sender=Attendance)
def attendance_deleted_handler(sender, instance, **kwargs):
    """Очищает кеш после удаления записи о посещаемости."""
    invalidate_attendance_cache(instance)