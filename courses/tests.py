import logging
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from courses.models import Course
from users.models import CustomUser
from django.core.cache import cache
import time
from rest_framework.permissions import BasePermission

logger = logging.getLogger('course')

class IsTeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['teacher', 'admin']

class CourseTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """Создание базовых данных для всех тестов"""
        cls.teacher_user = CustomUser.objects.create_user(
            email='teacher@example.com',
            username='teacher',
            password='password',
            role='teacher'
        )
        cls.student_user = CustomUser.objects.create_user(
            email='student@example.com',
            username='student',
            password='password',
            role='student'
        )
        cls.course_data = {
            'name': 'Django',
            'description': 'Django Course',
            'instructor': cls.teacher_user.id
        }
        cls.course = Course.objects.create(
            name='IT Audit',
            description='IT Audit Course',
            instructor=cls.teacher_user
        )
        cls.url = reverse('course-list')

    def setUp(self):
        """Принудительная аутентификация для каждого теста"""
        self.client.force_authenticate(user=self.teacher_user)

    def test_create_course(self):
        """Тест на создание курса"""
        response = self.client.post(self.url, self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)

    def test_update_course(self):
        """Тест на обновление курса"""
        url = reverse('course-detail', args=[self.course.id])
        updated_data = {'name': 'Advanced Django'}
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, 'Advanced Django')

    def test_delete_course(self):
        """Тест на удаление курса"""
        url = reverse('course-detail', args=[self.course.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.count(), 0)


class CoursePermissionsTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """Создание данных для тестов прав доступа"""
        cls.teacher_user = CustomUser.objects.create_user(
            email='teacher@example.com',
            username='teacher',
            password='password',
            role='teacher'
        )
        cls.student_user = CustomUser.objects.create_user(
            email='student@example.com',
            username='student',
            password='password',
            role='student'
        )
        cls.course_data = {
            'name': 'Django',
            'description': 'Django Course',
            'instructor': cls.teacher_user.id
        }
        cls.course_url = reverse('course-list')

    def setUp(self):
        """Принудительная аутентификация для каждого теста"""
        self.client.force_authenticate(user=self.teacher_user)

    def test_student_cannot_create_course(self):
        """Тест на запрет создания курса для студента"""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self.course_url, self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_create_course(self):
        """Тест на разрешение создания курса для учителя"""
        response = self.client.post(self.course_url, self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CourseCachingTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """Создание базовых данных для тестов кэширования"""
        cls.teacher_user = CustomUser.objects.create_user(
            email='teacher@example.com',
            username='teacher',
            password='password',
            role='teacher'
        )
        cls.course_data = {
            'name': 'Java',
            'description': 'Java Course',
            'instructor': cls.teacher_user.id
        }
        cls.course_url = reverse('course-list')

    def setUp(self):
        """Принудительная аутентификация для каждого теста"""
        self.client.force_authenticate(user=self.teacher_user)
        Course.objects.create(
            name='Java',
            description='Spring Course',
            instructor=self.teacher_user
        )

def test_course_list_caching(self):
        """Тест на кэширование списка курсов"""
        cache.clear()  

        # Первый запрос
        start_time = time.time()
        response1 = self.client.get(self.course_url)
        first_duration = time.time() - start_time


        cache.set(f"course_list_{self.teacher_user.id}", response1.data, timeout=60)

        # Второй запрос (должен быть быстрее)
        start_time = time.time()
        response2 = self.client.get(self.course_url)
        second_duration = time.time() - start_time

        self.assertEqual(response1.data, response2.data)
        self.assertTrue(second_duration <= first_duration)

        cached_data = cache.get(f"course_list_{self.teacher_user.id}")
        self.assertIsNotNone(cached_data)  
        self.assertEqual(cached_data, response1.data)
