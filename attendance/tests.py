# additional test cases

# from venv import logger
# from rest_framework.test import APITestCase
# from rest_framework import status
# from users.models import User
# from courses.models import Course
# from attendance.models import Attendance

# class AttendanceAPITests(APITestCase):
#     def setUp(self):
#         logger.info("Creating test data for Attendance API tests.")
#         self.teacher = User.objects.create_user(
#             email="teacher2@example.com",
#             password="password123",
#             role="teacher",
#             username="teacher2"  
#         )

#         self.student = User.objects.create_user(
#             email="student2@example.com",
#             password="password123",
#             role="student",
#             username="student2" 
#         )
        
#         self.admin = User.objects.create_user(
#             email="admin@example.com",
#             password="admin123",
#             role="admin",
#             username="admin"  
#         )

#         self.course = Course.objects.create(
#             name="Django",
#             description="Django Course",
#             instructor=self.teacher
#         )
     
#         self.attendance = Attendance.objects.create(
#             student=self.student,
#             course=self.course,
#             date="2024-11-20",
#             status="present"
#         )

#         self.teacher_token = self.client.post(
#             "/api/users/auth/jwt/create/",
#             {"email": "teacher2@example.com", "password": "password123"}
#         ).data["access"]
#         self.student_token = self.client.post(
#             "/api/users/auth/jwt/create/",
#             {"email": "student2@example.com", "password": "password123"}
#         ).data["access"]
#         self.admin_token = self.client.post(
#             "/api/users/auth/jwt/create/",
#             {"email": "admin@example.com", "password": "admin123"}
#         ).data["access"]
#         logger.info("Test setup complete.")

#     def test_teacher_can_mark_attendance(self):
#         logger.info(f"Teacher (id={self.teacher.id}) is attempting to mark attendance for student (id={self.student.id}) in course (id={self.course.id}) on 2024-11-18.")
#         response = self.client.post("/api/attendance/", {
#             "student": self.student.id,
#             "course": self.course.id,
#             "date": "2024-11-18", 
#             "status": "present"
#         })
#         if response.status_code == status.HTTP_201_CREATED:
#             logger.info(f"Attendance marked successfully for student (id={self.student.id}) in course (id={self.course.id}).")
#         else:
#             logger.error(f"Failed to mark attendance: {response.data}")
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_student_can_view_own_attendance(self):
#         logger.info(f"Student (id={self.student.id}) requested attendance details for record (id={self.attendance.id}).")
#         response = self.client.get(f"/api/attendance/{self.attendance.id}/")
#         if response.status_code == status.HTTP_200_OK:
#             logger.info(f"Attendance details retrieved successfully for record (id={self.attendance.id}).")
#         else:
#             logger.error(f"Failed to retrieve attendance details: {response.data}")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_admin_can_view_all_attendance(self):
#         logger.info(f"Admin (id={self.admin.id}) requested all attendance records.")
#         response = self.client.get("/api/attendance/")
#         if response.status_code == status.HTTP_200_OK:
#             logger.info(f"Total {len(response.data)} attendance records retrieved successfully.")
#         else:
#             logger.error(f"Failed to retrieve attendance records: {response.data}")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)