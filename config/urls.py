from django.contrib import admin
from django.urls import path

from students.views import (
    dashboard,
    student_list,
    student_create,
    student_update,
    student_delete,
    student_dashboard,
)

from courses.views import (
    course_list,
    course_create,
    course_update,
    course_delete,
    enrollment_list,
    enrollment_create,
    enrollment_delete,
    attendance,
    student_academic_record,
    result_list,
    result_create,
    result_update,
    result_delete,
)

from teachers.views import (
    teacher_dashboard,
    teacher_list,
    teacher_create,
    teacher_update,
    teacher_delete,
)

from accounts.views import (
    login_view,
    logout_view,
)


urlpatterns = [

    # ========================================================
    # LOGIN / LOGOUT
    # ========================================================

    path(
        'login/',
        login_view,
        name='login'
    ),

    path(
        'logout/',
        logout_view,
        name='logout'
    ),


    # ========================================================
    # MAIN DASHBOARD
    # ========================================================

    path(
        '',
        dashboard,
        name='dashboard'
    ),


    # ========================================================
    # DJANGO ADMIN
    # ========================================================

    path(
        'admin/',
        admin.site.urls
    ),


    # ========================================================
    # STUDENT MANAGEMENT
    # ========================================================

    path(
        'students/',
        student_list,
        name='student_list'
    ),

    path(
        'students/add/',
        student_create,
        name='student_create'
    ),

    path(
        'students/<int:student_id>/edit/',
        student_update,
        name='student_update'
    ),

    path(
        'students/<int:student_id>/delete/',
        student_delete,
        name='student_delete'
    ),

    path(
        'students/<int:student_id>/academic-record/',
        student_academic_record,
        name='student_academic_record'
    ),

    path(
        'student/dashboard/',
        student_dashboard,
        name='student_dashboard'
    ),


    # ========================================================
    # COURSE MANAGEMENT
    # ========================================================

    path(
        'courses/',
        course_list,
        name='course_list'
    ),

    path(
        'courses/add/',
        course_create,
        name='course_create'
    ),

    path(
        'courses/<int:course_id>/edit/',
        course_update,
        name='course_update'
    ),

    path(
        'courses/<int:course_id>/delete/',
        course_delete,
        name='course_delete'
    ),

    path(
        'courses/<int:course_id>/attendance/',
        attendance,
        name='attendance'
    ),


    # ========================================================
    # ENROLLMENT MANAGEMENT
    # ========================================================

    path(
        'enrollments/',
        enrollment_list,
        name='enrollment_list'
    ),

    path(
        'enrollments/add/',
        enrollment_create,
        name='enrollment_create'
    ),

    path(
        'enrollments/<int:enrollment_id>/delete/',
        enrollment_delete,
        name='enrollment_delete'
    ),


    # ========================================================
    # MARKS & GRADES
    # ========================================================

    path(
        'results/',
        result_list,
        name='result_list'
    ),

    path(
        'results/add/',
        result_create,
        name='result_create'
    ),

    path(
        'results/<int:result_id>/edit/',
        result_update,
        name='result_update'
    ),

    path(
        'results/<int:result_id>/delete/',
        result_delete,
        name='result_delete'
    ),


    # ========================================================
    # TEACHER MANAGEMENT
    # ========================================================

    # Teacher list
    path(
        'teachers/',
        teacher_list,
        name='teacher_list'
    ),

    # Add teacher
    path(
        'teachers/add/',
        teacher_create,
        name='teacher_create'
    ),

    # Edit teacher
    path(
        'teachers/<int:teacher_id>/edit/',
        teacher_update,
        name='teacher_update'
    ),

    # Delete teacher
    path(
        'teachers/<int:teacher_id>/delete/',
        teacher_delete,
        name='teacher_delete'
    ),

    # Teacher dashboard
    path(
        'teachers/<int:teacher_id>/dashboard/',
        teacher_dashboard,
        name='teacher_dashboard'
    ),
]