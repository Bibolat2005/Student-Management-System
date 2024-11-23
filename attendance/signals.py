import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Attendance
from django.core.cache import cache

# Настройка логирования
logger = logging.getLogger('attendance')

@receiver(post_save, sender=Attendance)
def log_attendance_marking(sender, instance, created, **kwargs):
    student_email = instance.student.user.email
    course_name = instance.course.name
    date = instance.date
    status = instance.status
    
    if created:
        logger.info(f"Attendance marked: student {student_email}, course {course_name},  date {date}, status {status}")
    else:
        logger.info(f"Attendance updated: student{student_email}, course {course_name}, date {date}, status {status}")

    invalidate_attendance_cache(instance)


@receiver(post_delete, sender=Attendance)
def log_attendance_deleted(sender, instance, **kwargs):
    logger.info(f"Attendance record deleted: course {instance.course.name}, date {instance.date}")
    invalidate_attendance_cache(instance)

# Функция для очистки кеша
def invalidate_attendance_cache(instance):
    cache.delete('attendance_list')
    cache_key = f'attendance_detail_{instance.pk}'
    cache.delete(cache_key)
