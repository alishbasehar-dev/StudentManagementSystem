from django.contrib import admin

from .models import (
    Course,
    Enrollment,
    Attendance,
    Result,
)


# ============================================================
# COURSE ADMIN
# ============================================================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = (
        'course_code',
        'course_name',
        'department',
        'credit_hours',
        'semester',
        'teacher',
        'is_active',
    )

    search_fields = (
        'course_code',
        'course_name',
        'department',
        'teacher__user__first_name',
        'teacher__user__last_name',
    )

    list_filter = (
        'department',
        'semester',
        'credit_hours',
        'is_active',
    )

    ordering = (
        'course_code',
    )


# ============================================================
# ENROLLMENT ADMIN
# ============================================================

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'course',
        'enrollment_date',
        'is_active',
    )

    search_fields = (
        'student__student_id',
        'student__user__first_name',
        'student__user__last_name',
        'course__course_code',
        'course__course_name',
    )

    list_filter = (
        'is_active',
        'course',
        'enrollment_date',
    )

    ordering = (
        '-enrollment_date',
    )


# ============================================================
# ATTENDANCE ADMIN
# ============================================================

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        'get_student',
        'get_course',
        'date',
        'status',
        'remarks',
    )

    search_fields = (
        'enrollment__student__student_id',
        'enrollment__student__user__first_name',
        'enrollment__student__user__last_name',
        'enrollment__course__course_code',
        'enrollment__course__course_name',
    )

    list_filter = (
        'status',
        'date',
        'enrollment__course',
    )

    ordering = (
        '-date',
    )

    @admin.display(description='Student')
    def get_student(self, obj):
        return obj.enrollment.student.user.get_full_name()

    @admin.display(description='Course')
    def get_course(self, obj):
        return obj.enrollment.course.course_code


# ============================================================
# RESULT ADMIN
# ============================================================

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):

    list_display = (
        'get_student',
        'get_course',
        'exam_type',
        'exam_name',
        'obtained_marks',
        'total_marks',
        'get_percentage',
        'grade',
    )

    search_fields = (
        'enrollment__student__student_id',
        'enrollment__student__user__first_name',
        'enrollment__student__user__last_name',
        'enrollment__course__course_code',
        'exam_name',
    )

    list_filter = (
        'exam_type',
        'grade',
        'enrollment__course',
    )

    ordering = (
        '-created_at',
    )

    @admin.display(description='Student')
    def get_student(self, obj):
        return obj.enrollment.student.user.get_full_name()

    @admin.display(description='Course')
    def get_course(self, obj):
        return obj.enrollment.course.course_code

    @admin.display(description='Percentage')
    def get_percentage(self, obj):
        return f"{obj.calculate_percentage():.2f}%"