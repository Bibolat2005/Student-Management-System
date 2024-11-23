import logging
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import django_filters
from django_filters.rest_framework import DjangoFilterBackend

from users.permissions import IsAdmin, IsTeacher

from .models import Student
from .serializers import StudentSerializer

class StudentPagination(PageNumberPagination):
    page_size = 10

logger = logging.getLogger('project')

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StudentPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user__username', 'dob']
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a list of students with filtering and pagination support.",
        responses={200: StudentSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('user__username', openapi.IN_QUERY, description="Filter by username", type=openapi.TYPE_STRING),
            openapi.Parameter('dob', openapi.IN_QUERY, description="Filter by date of birth", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        ]
    )

    
    def list(self, request, *args, **kwargs):
        cache_key = f"students_list_{request.GET.urlencode()}"
        logger.debug(f"Cache Key for students: {cache_key}")

        cached_students = cache.get(cache_key)
        if cached_students:
            logger.debug("Serving from cache")
            return Response(cached_students, status=status.HTTP_200_OK)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        logger.debug("Stored to cache")
        return response



    @swagger_auto_schema(
        operation_description="Create a new student.",
        request_body=StudentSerializer,
        responses={201: StudentSerializer, 400: "Bad request"}
    )
    def perform_create(self, serializer):
        super().perform_create(serializer)
        cache.delete_pattern("students_list_*")

    @swagger_auto_schema(
        operation_description="Update a student record.",
        request_body=StudentSerializer,
        responses={200: StudentSerializer, 400: "Bad request", 404: "Not found"}
    )
    def perform_update(self, serializer):
        super().perform_update(serializer)
        cache.delete_pattern("students_list_*")

    @swagger_auto_schema(
        operation_description="Delete a student record.",
        responses={204: "No content", 404: "Not found"}
    )
    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        cache.delete_pattern("students_list_*")

    
    def get_student_profile(request, student_id):
        cache_key = f"student_profile_{student_id}"
        student_profile = cache.get(cache_key)  
        if not student_profile:
            logger.info(f"Cache miss for student profile {student_id}. Fetching from database.")
            student = get_object_or_404(Student, id=student_id)
            student_profile = {
                "id": student.id,
                "name": student.first_name,
                "dob": student.dob,
                "is_active": student.is_active,
            }

            cache.set(cache_key, student_profile, timeout=1800)
            logger.info(f"Student profile {student_id} cached.")

        else:
            logger.info(f"Cache hit for student profile {student_id}.")

            return JsonResponse({"student_profile": student_profile})



    @action(detail=False, methods=['get', 'put', 'patch'], url_path='profile')
    @method_decorator(cache_page(60 * 15))
    def profile(self, request):
        user = request.user

        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            logger.warning(f"Student profile not found for user {user.id}.")
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            logger.info(f"User {user.id} accessed their profile.")
            serializer = self.get_serializer(student)
            return Response(serializer.data)

        if request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(student, data=request.data, partial=partial)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"User {user.id} updated their profile.")
                return Response(serializer.data)
            logger.error(f"Error updating profile for user {user.id}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(student, data=request.data, partial=partial)
            if serializer.is_valid():
                serializer.save()

                cache_key = f"student_profile_{student.id}"
                updated_data = serializer.data
                cache.set(cache_key, updated_data, timeout=60 * 15)
                logger.info(f"Cache updated for student profile {student.id}.")

                list_key = "student_profiles_list"
                student_list = cache.get(list_key, [])
                student_list = [item for item in student_list if item["id"] != student.id] 
                student_list.append(updated_data) 
                cache.set(list_key, student_list, timeout=60 * 15)
                logger.info(f"Student {student.id} added/updated in cached list.")

                return Response(serializer.data)

            logger.error(f"Error updating profile for user {user.id}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
