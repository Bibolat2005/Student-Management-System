from django.db import models
from django.contrib.auth.models import AbstractUser
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)
    is_teacher = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    

class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


    def __str__(self):
        return self.user.username
    
    def __str__(self):
        return self.username

    def is_teacher(self):
        return self.role == self.TEACHER

    def is_student(self):
        return self.role == self.STUDENT

    def is_admin(self):
        return self.role == self.ADMIN