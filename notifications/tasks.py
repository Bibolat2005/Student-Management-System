from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from users.models import CustomUser
from students.models import Student
from grades.models import Grade
from attendance.models import Attendance

@shared_task
def send_attendance_reminder_to_students():
    students_list = CustomUser.objects.filter(role='student')
    for student in students_list:
        send_mail(
            'Attendance Reminder',
            'Please ensure you mark your attendance for today.',
            'system@kbtu.kz',
            [student.email],
            fail_silently=False,
        )

@shared_task
def notify_grade_update(student_email, course_title, new_grade):
    subject = f'Updated Grade for {course_title}'
    message = f'Your grade for {course_title} has been updated to {new_grade}.'
    
    send_mail(
        subject,
        message,
        'system@kbtu.kz',
        [student_email],
        fail_silently=False,
    )

@shared_task
def send_performance_summary():
    students_list = CustomUser.objects.filter(role='student')
    for student in students_list:
        grades = Grade.objects.filter(student__user=student)
        performance_message = 'Here is a summary of your current grades:\n'
        
        for grade in grades:
            performance_message += f'{grade.course.name}: {grade.grade}\n'
        
        send_mail(
            'Weekly Performance Summary',
            performance_message,
            'system@kbtu.kz',
            [student.email],
            fail_silently=False,
        )

@shared_task
def generate_daily_report_for_admins():
    current_date = timezone.now().date()
    all_students = Student.objects.all()

    daily_report_data = []

    for student in all_students:
        attendance_record = Attendance.objects.filter(student=student, date=current_date).first()
        attendance_status = attendance_record.status if attendance_record else 'No Data Available'

        student_grades = Grade.objects.filter(student=student)

        student_info = f"Name: {student.user.get_full_name()}\n" \
                       f"Email: {student.user.email}\n" \
                       f"Attendance: {attendance_status}\n" \
                       f"Grades: "
        
        for grade in student_grades:
            student_info += f'{grade.course.name}: {grade.grade}\n'
        
        daily_report_data.append(student_info)

    report_subject = f'Daily Report for {current_date.strftime("%d.%m.%Y")}'
    recipients = [admin.email for admin in CustomUser.objects.filter(role='admin')]

    send_mail(
        report_subject,
        '\n'.join(daily_report_data),
        'system@kbtu.kz',
        recipients,
        fail_silently=False,
    )
