import logging
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from courses.permissions import IsTeacherOrAdmin
from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer
from users.permissions import IsAdmin, IsTeacher
import django_filters

logger = logging.getLogger('project')

class CourseCreateView(APIView):
    @swagger_auto_schema(
        operation_summary="Course Creation",
        operation_description="Allows administrators to create new courses.",
        request_body=CourseSerializer,
        responses={
            201: openapi.Response(description="Course created successfully"),
            400: "Data validation error",
        },
    )
    def post(self, request):
        logger.info(f"User {request.user.id} is attempting to create a course.")
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            course = serializer.save()
            logger.info(f"Course {course.id} successfully created by user {request.user.id}.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning(f"Course creation failed for user {request.user.id}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsTeacherOrAdmin]

    @swagger_auto_schema(
        operation_summary="Create Course",
        operation_description="Creates a new course. Available only to administrators or teachers.",
        responses={201: CourseSerializer}
    )
    def perform_create(self, serializer):
        user = self.request.user
        logger.info(f"User {user.id} is attempting to create a course.")
        serializer.save(instructor=user)
        logger.info(f"Course successfully created by user {user.id}.")

    def destroy(self, request, *args, **kwargs):
        course = self.get_object()
        logger.info(f"User {request.user.id} is attempting to delete course {course.id}.")
        if not (IsTeacher().has_permission(request, self) or IsAdmin().has_permission(request, self)):
            logger.error(f"Permission denied for user {request.user.id} to delete course {course.id}.")
            raise PermissionDenied("Only teachers or admins can delete courses.")
        response = super().destroy(request, *args, **kwargs)
        logger.info(f"Course {course.id} successfully deleted by user {request.user.id}.")
        return response

    @method_decorator(cache_page(60 * 60))
    @swagger_auto_schema(
        operation_summary="List of courses",
        operation_description="Returns a list of all courses with pagination.",
    )
    @method_decorator(cache_page(60 * 15)) 
    def list(self, request, *args, **kwargs):
        logger.debug(f"User {request.user.id} requested the course list.")
        return super().list(request, *args, **kwargs)


class EnrollmentViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_student:
            logger.debug(f"Fetching enrollments for student {user.id}.")
            return Enrollment.objects.filter(student=user).select_related('course')
        logger.debug(f"Fetching all enrollments for user {user.id} (admin or teacher).")
        return Enrollment.objects.all()


    @swagger_auto_schema(
        operation_summary="Student Enrollment",
        operation_description="Allows a student to enroll in a course. If the student is already enrolled, an error will be returned.",
        request_body=EnrollmentSerializer,
        responses={201: openapi.Response(description="Enrollment successful"),
                   400: "Error while attempting to enroll"},
    )
    def perform_create(self, serializer):
        user = self.request.user
        course = serializer.validated_data.get('course')
        if Enrollment.objects.filter(student=user, course=course).exists():
            logger.warning(f"User {user.id} attempted to enroll in course {course.id} but is already enrolled.")
            raise PermissionDenied("You are already enrolled in this course.")
        logger.info(f"User {user.id} is enrolling in course {course.id}.")
        serializer.save(student=user)
        logger.info(f"User {user.id} successfully enrolled in course {course.id}.")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            logger.info(f"Enrollment created successfully for user {request.user.id}.")
            return Response({"message": "You have been successfully enrolled!"}, status=201)
        logger.error(f"Enrollment creation failed for user {request.user.id}.")
        return response
    


    @swagger_auto_schema(
        operation_summary="List enrollments",
        operation_description="Returns a paginated list of enrollments for the current user.",
        responses={
            200: openapi.Response(
                description="List of enrollments",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Enrollment ID"),
                            'course': openapi.Schema(type=openapi.TYPE_STRING, description="Course name"),
                            'status': openapi.Schema(type=openapi.TYPE_STRING, description="Enrollment status"),
                        }
                    )
                )
            )
        }
    )
    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        """
        List enrollments with caching and pagination.
        """
        user = self.request.user
        logger.info(f"User {user.id} requested enrollment list.")
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

    
class CoursePagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size' 
    max_page_size = 100 

class CourseListView(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePagination


class CourseFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Course Name') 
    instructor = django_filters.CharFilter(lookup_expr='icontains', label='Instructor Name')

    class Meta:
        model = Course
        fields = ['name', 'instructor']

class CourseListView(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filterset_class = CourseFilter  
    pagination_class = CoursePagination 
    @swagger_auto_schema(
        operation_summary="Список курсов с фильтрацией",
        operation_description="Возвращает список курсов с поддержкой фильтрации и пагинации.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)