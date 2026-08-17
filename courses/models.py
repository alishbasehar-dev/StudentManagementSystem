from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal

from teachers.models import Teacher
from students.models import Student


# ============================================================
# COURSE MODEL
# ============================================================

class Course(models.Model):

    course_code = models.CharField(
        max_length=20,
        unique=True
    )

    course_name = models.CharField(
        max_length=150
    )

    description = models.TextField(
        blank=True
    )

    credit_hours = models.PositiveIntegerField(
        default=3,
        validators=[
            MinValueValidator(1)
        ]
    )

    semester = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1)
        ]
    )

    department = models.CharField(
        max_length=100
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses'
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.course_code} - "
            f"{self.course_name}"
        )


# ============================================================
# ENROLLMENT MODEL
# ============================================================

class Enrollment(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    enrollment_date = models.DateField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    'student',
                    'course'
                ],
                name='unique_student_course'
            )
        ]

        ordering = [
            '-enrollment_date'
        ]

    def __str__(self):

        try:

            student_name = (
                self.student.user.get_full_name()
            )

            if not student_name:

                student_name = (
                    self.student.user.username
                )

        except Exception:

            student_name = str(
                self.student.student_id
            )

        return (
            f"{student_name} "
            f"({self.student.student_id}) - "
            f"{self.course.course_code}"
        )


# ============================================================
# ATTENDANCE MODEL
# ============================================================

class Attendance(models.Model):

    ATTENDANCE_STATUS = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Leave', 'Leave'),
    ]

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )

    date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=ATTENDANCE_STATUS,
        default='Present'
    )

    remarks = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    'enrollment',
                    'date'
                ],
                name='unique_attendance_per_day'
            )
        ]

        ordering = [
            '-date'
        ]

    def __str__(self):

        return (
            f"{self.enrollment.student.student_id} - "
            f"{self.enrollment.course.course_code} - "
            f"{self.date} - "
            f"{self.status}"
        )


# ============================================================
# RESULT / MARKS MODEL
# ============================================================

class Result(models.Model):

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='results'
    )

    exam_type = models.CharField(
        max_length=50
    )

    exam_name = models.CharField(
        max_length=100
    )

    obtained_marks = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0'))
        ]
    )

    total_marks = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01'))
        ]
    )

    grade = models.CharField(
        max_length=5,
        blank=True
    )

    remarks = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = [
            '-created_at'
        ]

    # ========================================================
    # VALIDATION
    # ========================================================

    def clean(self):

        super().clean()

        if (
            self.obtained_marks is not None
            and self.obtained_marks < 0
        ):

            raise ValidationError({
                'obtained_marks':
                    'Obtained marks cannot be negative.'
            })

        if (
            self.total_marks is not None
            and self.total_marks <= 0
        ):

            raise ValidationError({
                'total_marks':
                    'Total marks must be greater than zero.'
            })

        if (
            self.obtained_marks is not None
            and self.total_marks is not None
            and self.obtained_marks > self.total_marks
        ):

            raise ValidationError({
                'obtained_marks':
                    'Obtained marks cannot be greater than total marks.'
            })

    # ========================================================
    # PERCENTAGE
    # ========================================================

    def calculate_percentage(self):

        if not self.total_marks:

            return Decimal('0')

        return (
            self.obtained_marks /
            self.total_marks
        ) * Decimal('100')

    # ========================================================
    # GRADE
    # ========================================================

    def calculate_grade(self):

        percentage = self.calculate_percentage()

        if percentage >= 85:

            return 'A'

        elif percentage >= 80:

            return 'A-'

        elif percentage >= 75:

            return 'B+'

        elif percentage >= 70:

            return 'B'

        elif percentage >= 65:

            return 'B-'

        elif percentage >= 60:

            return 'C+'

        elif percentage >= 55:

            return 'C'

        elif percentage >= 50:

            return 'C-'

        elif percentage >= 40:

            return 'D'

        else:

            return 'F'

    # ========================================================
    # SAVE
    # ========================================================

    def save(self, *args, **kwargs):

        self.full_clean()

        self.grade = self.calculate_grade()

        super().save(
            *args,
            **kwargs
        )

    # ========================================================
    # STRING REPRESENTATION
    # ========================================================

    def __str__(self):

        return (
            f"{self.enrollment.student.student_id} - "
            f"{self.enrollment.course.course_code} - "
            f"{self.exam_name}"
        )