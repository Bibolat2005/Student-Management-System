# grades/signals.py

import logging
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from .models import Grade

logger = logging.getLogger('grades')

@receiver(post_save, sender=Grade)
def log_grade_update(sender, instance, created, **kwargs):
    student_email = instance.student.user.email
    course_name = instance.course.name
    grade_value = instance.grade
    teacher_email = instance.teacher.email
    if created:
        logger.info(f"A new grade has been added for the student {student_email}, course: {course_name},  grade:  {grade_value}, teacher {teacher_email}")
    else:
        logger.info(f"The grade has been updated for the student {student_email}, course: {course_name}, new grade {grade_value}, teacher {teacher_email}")


@receiver(post_delete, sender=Grade)
def log_grade_deleted(sender, instance, **kwargs):
    logger.info(f"The grade has been deleted for the student: {instance.student.email}, course: {instance.course.name}")