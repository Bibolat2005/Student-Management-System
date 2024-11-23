# from rest_framework.test import APITestCase
# from rest_framework import status
# from django.urls import reverse
# from users.models import CustomUser
# from students.models import Student
# from courses.models import Course
# from grades.models import Grade
# from datetime import date

# class GradeViewSetTestCase(APITestCase):
#     def setUp(self):
#         self.admin_user = CustomUser.objects.create_user(
#         username='admin',  
#         email='admin@example.com', 
#         password='admin123', 
#         role='admin'
#     )
#         self.teacher_user = CustomUser.objects.create_user(
#         username='teacher', 
#         email='teacher@example.com', 
#         password='teacher123', 
#         role='teacher'
#     )
#         self.student_user = CustomUser.objects.create_user(
#         username='student', 
#         email='student@example.com', 
#         password='student123', 
#         role='student'
#     )
#         self.student = Student.objects.create(user=self.student_user, name='Test Student')
#         self.course = Course.objects.create(name='Test Course', description='Description of the course')

#         self.grade = Grade.objects.create(
#         student=self.student,
#         course=self.course,
#         grade=90,
#         date=date.today(),
#         teacher=self.teacher_user
#     )

#         self.grade_list_url = reverse('grades-list')  
#         self.grade_detail_url = reverse('grades-detail', args=[self.grade.id])  

#     def test_list_grades_as_admin(self):
#         self.client.login(email='admin@example.com', password='admin123')

#         response = self.client.get(self.grade_list_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)

#     def test_create_grade_as_teacher(self):
#         self.client.login(email='teacher@example.com', password='teacher123')

#         data = {
#             'student': self.student.id,
#             'course': self.course.id,
#             'grade': 69,
#             'date': date.today(),
#             'teacher': self.teacher_user.id,
#         }

#         response = self.client.post(self.grade_list_url, data)

#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data['grade'], 69)

#     def test_retrieve_grade_as_student(self):
#         self.client.login(email='student@example.com', password='student123')
#         response = self.client.get(self.grade_detail_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['grade'], 100)

#     def test_update_grade_as_teacher(self):
#         self.client.login(email='teacher@example.com', password='teacher123')

#         data = {
#             'student': self.student.id,
#             'course': self.course.id,
#             'grade': 50,
#             'date': date.today(),
#             'teacher': self.teacher_user.id,
#         }
#         response = self.client.put(self.grade_detail_url, data)

    
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['grade'], 75)

#     def test_delete_grade_as_teacher(self):
#         self.client.login(email='teacher@example.com', password='teacher123')
#         response = self.client.delete(self.grade_detail_url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertFalse(Grade.objects.filter(id=self.grade.id).exists())