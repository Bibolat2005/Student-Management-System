from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now
from students.models import Student
from grades.models import Grade
from attendance.models import Attendance

@shared_task
def daily_attendance_reminder():
    students = Student.objects.all()
    for student in students:
        send_mail(
            'Daily Attendance Reminder',
            'Please mark your attendance for today.',
            'noreply@example.com',
            [student.user.email],
            fail_silently=False,
        )
    return f"Sent reminders to {students.count()} students."

@shared_task
def grade_update_notification(student_id, course_name, grade):
    student = Student.objects.get(id=student_id)
    send_mail(
        'Grade Update Notification',
        f'Your grade for {course_name} has been updated to {grade}.',
        'noreply@example.com',
        [student.user.email],
        fail_silently=False,
    )
    return f"Notified {student.user.email} about grade update."

@shared_task
def daily_report():
    attendance_count = Attendance.objects.filter(date=now().date()).count()
    grades_count = Grade.objects.filter(date=now().date()).count()
    send_mail(
        'Daily Report',
        f'Today, {attendance_count} attendance records and {grades_count} grades were processed.',
        'noreply@example.com',
        ['admin@example.com'],
        fail_silently=False,
    )
    return f"Daily report sent."

@shared_task
def weekly_performance_email():
    students = Student.objects.all()
    for student in students:
        attendance = Attendance.objects.filter(student=student).count()
        grades = Grade.objects.filter(student=student)
        grade_summary = "\n".join([f"{g.course.name}: {g.grade}" for g in grades])
        email_body = (
            f"Weekly Performance Summary\n\n"
            f"Attendance Count: {attendance}\n"
            f"Grades:\n{grade_summary}"
        )
        send_mail(
            'Weekly Performance Summary',
            email_body,
            'noreply@example.com',
            [student.user.email],
            fail_silently=False,
        )
    return f"Weekly performance emails sent to {students.count()} students."