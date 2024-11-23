from django.test import TestCase
from ..models import Student
from django.contrib.auth import get_user_model

User = get_user_model()

class StudentModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser', password='12345')
        self.student = Student.objects.create(user=user, dob='2024-07-12')

    def test_student_creation(self):
        self.assertEqual(self.student.user.username, 'testuser')
        self.assertEqual(str(self.student), self.student.user.username)
