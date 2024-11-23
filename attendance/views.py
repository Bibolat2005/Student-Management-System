from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from attendance.serializers import AttendanceSerializer
from attendance.models import Attendance
from courses.models import Course
import logging
from rest_framework import viewsets

logger = logging.getLogger(__name__)

class AttendanceListView(APIView):
    """
    Список посещаемости для заданного курса.
    """
    course_id_param = openapi.Parameter(
        'course_id',
        openapi.IN_PATH,
        description="ID курса",
        type=openapi.TYPE_INTEGER
    )

    @swagger_auto_schema(
        manual_parameters=[course_id_param],
        responses={200: "Список посещаемости"}
    )
    def get(self, request, course_id, *args, **kwargs):
        try:
            course = get_object_or_404(Course, id=course_id)
            attendances = Attendance.objects.filter(course=course).select_related('student__user').values(
                'student__first_name', 'student__last_name', 'present'
            )
            logger.info(f"Attendance list retrieved for course: {course.name}, ID: {course_id}")

            return Response({
                "course": course.name,
                "attendances": [
                    {
                        "first_name": attendance['student__first_name'],
                        "last_name": attendance['student__last_name'],
                        "present": attendance['present']
                    }
                    for attendance in attendances
                ]
            })

        except Exception as e:
            logger.error(f"Error fetching attendance list for course ID {course_id}: {str(e)}")
            return Response({"error": "Error fetching attendance list"}, status=500)


class AttendanceCreateView(APIView):
    """
    Создание или обновление записи посещаемости.
    """
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'student_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID студента"),
                'present': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Присутствие (true/false)"),
            },
        ),
        responses={201: "Attendance created/updated", 400: "Invalid data"}
    )
    def post(self, request, course_id, *args, **kwargs):
        try:
            course = get_object_or_404(Course, id=course_id)
            student_id = request.data.get('student_id')
            present = request.data.get('present', False)

            if student_id:
                attendance, created = Attendance.objects.update_or_create(
                    course=course,
                    student_id=student_id,
                    defaults={"present": present}
                )
                action = "created" if created else "updated"
                logger.info(f"Attendance {action} for course: {course.name}, student ID: {student_id}, present: {present}")

                return Response({
                    "message": f"Attendance {action} successfully",
                    "attendance_id": attendance.id
                }, status=201)
            else:
                logger.error("Failed to create/update attendance: Missing student_id")
                return Response({"error": "Missing student_id"}, status=400)
        except Exception as e:
            logger.error(f"Error creating/updating attendance for course ID {course_id}: {str(e)}")
            return Response({"error": "Error creating/updating attendance"}, status=500)


class AttendanceUpdateView(APIView):
    """
    Получение и обновление записи посещаемости.
    """
    @swagger_auto_schema(
        responses={200: "Attendance retrieved", 404: "Attendance not found"}
    )
    def get(self, request, attendance_id, *args, **kwargs):
        try:
            attendance = get_object_or_404(Attendance, id=attendance_id)
            logger.info(f"Attendance record retrieved: ID {attendance_id}")
            return Response({
                "attendance_id": attendance.id,
                "student": f"{attendance.student.first_name} {attendance.student.last_name}",
                "course": attendance.course.name,
                "present": attendance.present
            })
        except Exception as e:
            logger.error(f"Error retrieving attendance ID {attendance_id}: {str(e)}")
            return Response({"error": "Attendance not found"}, status=404)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'present': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Присутствие (true/false)"),
            },
        ),
        responses={200: "Attendance updated", 403: "Permission denied", 400: "Invalid data"}
    )
    def post(self, request, attendance_id, *args, **kwargs):
        try:
            attendance = get_object_or_404(Attendance, id=attendance_id)

            if not request.user.is_superuser and attendance.student.user != request.user:
                logger.warning(f"Permission denied for user {request.user.id} to update attendance ID {attendance_id}")
                return Response({"error": "Permission denied"}, status=403)

            present = request.data.get('present')
            if present is not None:
                attendance.present = present
                attendance.save()
                logger.info(f"Attendance updated: ID {attendance_id}, present: {attendance.present}")
                return Response({"message": "Attendance updated successfully"})
            else:
                logger.error(f"Failed to update attendance ID {attendance_id}: Missing 'present' field")
                return Response({"error": "Missing 'present' field"}, status=400)
        except Exception as e:
            logger.error(f"Error updating attendance ID {attendance_id}: {str(e)}")
            return Response({"error": "Error updating attendance"}, status=500)
        

    @swagger_auto_schema(
    responses={204: "Attendance deleted", 403: "Permission denied", 404: "Attendance not found"}
    )
    def delete(self, request, attendance_id, *args, **kwargs):
        try:
            attendance = get_object_or_404(Attendance, id=attendance_id)

            # Check if the user has permission to delete the attendance record
            if not request.user.is_superuser and attendance.student.user != request.user:
                logger.warning(f"Permission denied for user {request.user.id} to delete attendance ID {attendance_id}")
                return Response({"error": "Permission denied"}, status=403)

            # Perform the deletion
            attendance.delete()
            logger.info(f"Attendance deleted: ID {attendance_id}")
            return Response({"message": "Attendance deleted successfully"}, status=204)
        except Exception as e:
            logger.error(f"Error deleting attendance ID {attendance_id}: {str(e)}")
            return Response({"error": "Error deleting attendance"}, status=500)


class AttendanceMarkingView(APIView):
    """
    Быстрая запись посещаемости с логированием.
    """

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'student_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID студента"),
                'present': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Присутствие (true/false)"),
            },
        ),
        responses={200: openapi.Response(description="Attendance recorded successfully"),
                   400: openapi.Response(description="Invalid data")}
    )
    def post(self, request, *args, **kwargs):
        try:
            course_id = kwargs.get('course_id')
            student_id = request.data.get('student_id')
            present = request.data.get('present', False)

            if not student_id:
                logger.error("Failed to mark attendance: Missing student_id")
                return Response({'error': 'Missing student_id'}, status=400)

            attendance, created = Attendance.objects.update_or_create(
                course_id=course_id,
                student_id=student_id,
                defaults={'present': present}
            )

            action = "created" if created else "updated"
            logger.info(
                f"Attendance {action} for course: {course_id}, student ID: {student_id}, present: {present}"
            )

            return Response({'message': 'Attendance recorded successfully'})
        except Exception as e:
            logger.error(f"Error marking attendance for course ID {course_id}: {str(e)}")
            return Response({"error": "Error marking attendance"}, status=500)

