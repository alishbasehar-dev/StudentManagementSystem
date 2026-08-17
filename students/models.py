from django.conf import settings
from django.db import models


class Student(models.Model):

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    student_id = models.CharField(
        max_length=20,
        unique=True
    )

    phone = models.CharField(
        max_length=20
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    address = models.TextField(
        blank=True
    )

    department = models.CharField(
        max_length=100
    )

    program = models.CharField(
        max_length=100
    )

    semester = models.PositiveIntegerField()

    enrollment_date = models.DateField(
        auto_now_add=True
    )

    profile_picture = models.ImageField(
        upload_to='students/',
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"