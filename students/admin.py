from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        'student_id',
        'get_student_name',
        'department',
        'program',
        'semester',
        'gender',
    )

    search_fields = (
        'student_id',
        'user__first_name',
        'user__last_name',
        'user__email',
    )

    list_filter = (
        'department',
        'program',
        'semester',
        'gender',
    )

    def get_student_name(self, obj):
        return obj.user.get_full_name()

    get_student_name.short_description = 'Student Name'