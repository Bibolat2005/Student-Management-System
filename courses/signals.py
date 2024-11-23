# courses/signals.py

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Course, Enrollment

logger = logging.getLogger('courses')

@receiver(post_save, sender=Enrollment)
def log_course_enrollment(sender, instance, created, **kwargs):
    if created:
        student_email = instance.student.user.email
        course_name = instance.course.name
        logger.info(f" Student {student_email} enrolled in course {course_name}")


@receiver(post_save, sender=Course)
def log_course_created(sender, instance, created, **kwargs):
    if created:
        logger.info(f"New course created: {instance.name}, instructor: {instance.instructor.email}")
    else:
        logger.info(f"Course updated: {instance.name}, instructor: {instance.instructor.email}"
)


@receiver(post_delete, sender=Course)
def log_course_deleted(sender, instance, **kwargs):
    logger.info(f"Course deleted: {instance.name}, instructor: {instance.instructor.email}")