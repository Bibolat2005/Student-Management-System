# students/tests.py
# from django.test import TestCase
# from rest_framework.test import APIClient
# from rest_framework import status
# from django.contrib.auth import get_user_model
# from users.models import CustomUser
# from students.models import Student

# class StudentViewSetTests(TestCase):

#     def setUp(self):
#         # Создаем пользователя
#         self.user = get_user_model().objects.create_user(
#             username='testuser',
#             email='test@example.com',
#             password='password123'
#         )
#         self.client = APIClient()
#         self.client.login(username='testuser', password='password123')

#         # Создаем тестового студента
#         self.student = Student.objects.create(
#             user=self.user,
#             dob="2000-01-01"
#         )

#     def test_create_student_and_cache_clear(self):
#         response = self.client.post('/students/', {'dob': '2000-01-01'})
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_delete_student_and_cache_clear(self):
#         response = self.client.delete(f'/students/{self.student.id}/')
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

#     def test_list_students_with_cache(self):
#         response = self.client.get('/students/')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_permissions(self):
#         response = self.client.get('/students/')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_update_student_and_cache_clear(self):
#         response = self.client.put(f'/students/{self.student.id}/', {'dob': '2001-01-01'})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
