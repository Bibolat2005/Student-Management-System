import logging
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import action
from .models import Grade
from .serializers import GradeSerializer
from users.permissions import IsTeacher, IsAdmin
from django.db.models import Q


logger = logging.getLogger('grades')

class GradeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing grades:
    - List, create, update, delete grades.
    - Additional actions: update score for a grade.
    """
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Define permissions based on the action being performed.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsTeacher()]
        elif self.action == 'list':
            return [IsAuthenticated(), IsAdmin()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            if user.role == 'student':
                return Grade.objects.filter(student=user)
            else:
                return Grade.objects.all()
        else:
            return Grade.objects.none()

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('student_id', openapi.IN_QUERY, description="Filter by Student ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('course_id', openapi.IN_QUERY, description="Filter by Course ID", type=openapi.TYPE_INTEGER)
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Get a list of grades, with optional filters for student and course.
        Accessible to authenticated Admin and Teacher users.
        """
        queryset = self.filter_queryset(self.get_queryset())
        student_id = request.query_params.get('student_id')
        course_id = request.query_params.get('course_id')

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=GradeSerializer,
        responses={201: "Grade successfully created", 400: "Validation error"}
    )
    def create(self, request, *args, **kwargs):
        """
        Create a new grade entry for a student.
        Accessible to authenticated Teacher and Admin users.
        """
        serializer = GradeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Grade created: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=GradeSerializer,
        responses={200: "Grade successfully updated", 403: "Permission denied"}
    )
    def update(self, request, *args, **kwargs):
        """
        Update an existing grade entry.
        Accessible to Teacher and Admin users.
        """
        grade = self.get_object()
        if not self.has_permission_to_update(grade):
            return Response({"detail": "Permission denied to update this grade."}, status=status.HTTP_403_FORBIDDEN)

        serializer = GradeSerializer(grade, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Grade updated: {grade.student} - {grade.course} - {grade.grade}")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        responses={204: "Grade successfully deleted", 403: "Permission denied"}
    )
    def destroy(self, request, *args, **kwargs):
        """
        Delete a grade entry.
        Accessible to Teacher and Admin users.
        """
        grade = self.get_object()
        if not self.has_permission_to_delete(grade):
            return Response({"detail": "Permission denied to delete this grade."}, status=status.HTTP_403_FORBIDDEN)

        grade.delete()
        logger.info(f"Grade deleted: {grade.student} - {grade.course}")
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'score': openapi.Schema(type=openapi.TYPE_INTEGER, description="New grade score")}
        ),
        responses={200: "Score successfully updated", 404: "Grade not found"}
    )
    @action(detail=True, methods=['post'])
    def update_score(self, request, *args, **kwargs):
        """
        Update the score of a specific grade.
        Accessible to Teacher and Admin users.
        """
        grade = self.get_object()
        new_score = request.data.get('score')

        if new_score is None:
            return Response({"detail": "Score is required."}, status=status.HTTP_400_BAD_REQUEST)

        old_score = grade.score
        grade.score = new_score
        grade.save()

        logger.info(f"Score updated: {grade.student} - {grade.course} | Old: {old_score} -> New: {new_score}")
        return Response({"message": "Score updated successfully."}, status=status.HTTP_200_OK)

    def has_permission_to_update(self, grade):
        """
        Check if the user has permission to update the grade.
        """
        return self.request.user == grade.teacher or self.request.user.is_superuser

    def has_permission_to_delete(self, grade):
        """
        Check if the user has permission to delete the grade.
        """
        return self.request.user == grade.teacher or self.request.user.is_superuser
