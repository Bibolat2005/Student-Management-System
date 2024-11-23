from django.db import router
from rest_framework.routers import DefaultRouter
from rest_framework import viewsets
from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.AttendanceListView.as_view(), name='attendance-list'),
    path('create/', views.AttendanceCreateView.as_view(), name='attendance-create'),
    path('course/<int:course_id>/', views.AttendanceListView.as_view(), name='attendance_list'),
    path('course/<int:course_id>/create/', views.AttendanceCreateView.as_view(), name='attendance_create'),
    path('attendance/edit/<int:attendance_id>/', views.AttendanceUpdateView.as_view(), name='attendance_edit'),
    path('course/<int:course_id>/', views.AttendanceListView.as_view(), name='attendance_list'),
]


