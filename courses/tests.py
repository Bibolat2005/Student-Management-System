# import logging
# from rest_framework.test import APITestCase
# from django.urls import reverse
# from rest_framework import status
# from courses.models import Course
# from users.models import CustomUser
# from unittest.mock import patch


# class CourseTests(APITestCase):
#     @classmethod
#     def setUpTestData(cls):
#         """Создание базовых данных для всех тестов"""
#         cls.teacher_user = CustomUser.objects.create_user(
#             email='teacher@example.com',
#             username='teacher',
#             password='password',
#             role='teacher'
#         )
#         cls.course_data = {
#             'name': 'Django',
#             'description': 'Django Course',
#             'instructor': cls.teacher_user.id
#         }
#         cls.course = Course.objects.create(
#             name='IT Audit',
#             description='IT Audit Course',
#             instructor=cls.teacher_user
#         )
#         cls.url = reverse('course-list')

#     def setUp(self):
#         """Принудительная аутентификация для каждого теста"""
#         self.client.force_authenticate(user=self.teacher_user)

#     @patch('courses.views.logger')
#     def test_create_course_logging(self, mock_logger):
#         """Тест на создание курса с логированием"""
#         response = self.client.post(self.url, self.course_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Course.objects.count(), 2)

#         # Проверка вызова логов
#         mock_logger.info.assert_any_call(
#             f"User {self.teacher_user.id} is attempting to create a course."
#         )
#         mock_logger.info.assert_any_call(
#             f"Course {Course.objects.last().id} successfully created by user {self.teacher_user.id}."
#         )

#     @patch('courses.views.logger')
#     def test_delete_course_logging(self, mock_logger):
#         """Тест на удаление курса с логированием"""
#         url = reverse('course-detail', args=[self.course.id])
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertEqual(Course.objects.count(), 0)

#         # Проверка вызова логов
#         mock_logger.info.assert_any_call(
#             f"User {self.teacher_user.id} is attempting to delete course {self.course.id}."
#         )
#         mock_logger.info.assert_any_call(
#             f"Course {self.course.id} successfully deleted by user {self.teacher_user.id}."
#         )

#     @patch('courses.views.logger')
#     def test_update_course_logging(self, mock_logger):
#         """Тест на обновление курса с логированием"""
#         url = reverse('course-detail', args=[self.course.id])
#         updated_data = {'name': 'Advanced Django'}
#         response = self.client.patch(url, updated_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.course.refresh_from_db()
#         self.assertEqual(self.course.name, 'Advanced Django')

#         # Проверка вызова логов
#         mock_logger.info.assert_any_call(
#             f"Course updated: {self.course.name}, instructor: {self.course.instructor.email}"
#         )
