from django.contrib import admin
from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):

    list_display = (
        'teacher_id',
        'get_name',
        'department',
        'designation',
        'phone',
        'is_active',
    )

    search_fields = (
        'teacher_id',
        'user__first_name',
        'user__last_name',
        'user__email',
        'department',
    )

    list_filter = (
        'department',
        'designation',
        'is_active',
    )

    ordering = (
        'teacher_id',
    )

    def get_name(self, obj):
        return obj.user.get_full_name()

    get_name.short_description = 'Teacher Name'