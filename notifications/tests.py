from django.core import mail
from django.test import TestCase
from unittest.mock import patch
from users.models import CustomUser
from courses.models import Course
from grades.models import Grade
from attendance.models import Attendance
from students.models import Student
from django.utils import timezone
from notifications.tasks import (send_attendance_reminder_to_students, send_performance_summary,
                                 generate_daily_report_for_admins, notify_grade_update)


class SendAttendanceReminderToStudentsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student_bibo = CustomUser.objects.create_user(
            email='student_bibo@example.com',
            username='student1',
            password='password',
            role='student'
        )
        cls.student_iliyas = CustomUser.objects.create_user(
            email='student_iliyas@example.com',
            username='student2',
            password='password',
            role='student'
        )
        cls.teacher = CustomUser.objects.create_user(
            email='teacher@example.com',
            username='teacher',
            password='password',
            role='teacher'
        )

    def test_send_attendance_reminder_to_students(self):
        send_attendance_reminder_to_students()

        self.assertEqual(len(mail.outbox), 2)

        recipients = [email.to[0] for email in mail.outbox]
        self.assertIn('student_bibo@example.com', recipients)
        self.assertIn('student_iliyas@example.com', recipients)
        self.assertNotIn('teacher@example.com', recipients)

        for email in mail.outbox:
            self.assertEqual(email.subject, 'Attendance Reminder')
            self.assertEqual(email.body, 'Please ensure you mark your attendance for today.')
            self.assertEqual(email.from_email, 'system@kbtu.kz')


class NotificationTasksTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = CustomUser.objects.create_user(
            email='teacher@example.com', username='teacher', password='password', role='teacher'
        )
        cls.student_user = CustomUser.objects.create_user(
            email='student@example.com', username='student', password='password', role='student'
        )
        cls.student = Student.objects.create(user=cls.student_user)
        cls.course = Course.objects.create(name="Django", description="Django Course", instructor=cls.teacher)

    @patch('notifications.tasks.send_mail')
    def test_notify_grade_update(self, mock_send_mail):
        student_email = self.student_user.email
        course_title = 'Django'
        new_grade = 'A-'

        notify_grade_update(student_email, course_title, new_grade)

        mock_send_mail.assert_called_once_with(
            f'Updated Grade for {course_title}',
            f'Your grade for {course_title} has been updated to {new_grade}.',
            'system@kbtu.kz',
            [student_email],
            fail_silently=False,
        )

    @patch('notifications.tasks.send_mail')
    def test_send_performance_summary(self, mock_send_mail):
        Grade.objects.create(student=self.student, course=self.course, grade='B+', teacher_id=self.teacher.id)

        send_performance_summary()

        self.assertTrue(mock_send_mail.called)
        email_call_args = mock_send_mail.call_args[0]
        self.assertIn('Here is a summary of your current grades:', email_call_args[1])
        self.assertIn('Django: B+', email_call_args[1])

    @patch('notifications.tasks.send_mail')
    def test_generate_daily_report_for_admins(self, mock_send_mail):
        admin_user = CustomUser.objects.create_user(
            email='admin@example.com', username='admin', password='password', role='admin'
        )

        Attendance.objects.create(student=self.student, course=self.course, date=timezone.now().date(), status='Present')
        Grade.objects.create(student=self.student, course=self.course, grade='A', teacher_id=self.teacher.id)

        generate_daily_report_for_admins()

        self.assertTrue(mock_send_mail.called)
        email_call_args = mock_send_mail.call_args[0]
        self.assertIn('Daily Report', email_call_args[0])
        self.assertIn(admin_user.email, email_call_args[3])
