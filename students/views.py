from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Student

from courses.models import (
    Course,
    Enrollment,
    Attendance,
    Result,
)

from teachers.models import Teacher


User = get_user_model()


# ============================================================
# MAIN DASHBOARD
# ============================================================

def dashboard(request):

    # --------------------------------------------------------
    # BASIC COUNTS
    # --------------------------------------------------------

    total_students = Student.objects.count()

    total_teachers = Teacher.objects.count()

    total_courses = Course.objects.count()

    total_enrollments = Enrollment.objects.count()

    total_results = Result.objects.count()


    # --------------------------------------------------------
    # TODAY'S ATTENDANCE
    # --------------------------------------------------------

    today = timezone.localdate()

    today_present = Attendance.objects.filter(
        date=today,
        status='Present'
    ).count()

    today_absent = Attendance.objects.filter(
        date=today,
        status='Absent'
    ).count()

    today_late = Attendance.objects.filter(
        date=today,
        status='Late'
    ).count()

    today_leave = Attendance.objects.filter(
        date=today,
        status='Leave'
    ).count()


    # --------------------------------------------------------
    # ATTENDANCE PERCENTAGE
    # --------------------------------------------------------

    today_total = (
        today_present
        + today_absent
        + today_late
        + today_leave
    )

    if today_total > 0:
        today_attendance_percentage = (
            today_present / today_total
        ) * 100
    else:
        today_attendance_percentage = 0


    # --------------------------------------------------------
    # RECENT STUDENTS
    # --------------------------------------------------------

    recent_students = Student.objects.select_related(
        'user'
    ).order_by(
        '-id'
    )[:5]


    # --------------------------------------------------------
    # RECENT ENROLLMENTS
    # --------------------------------------------------------

    recent_enrollments = Enrollment.objects.select_related(
        'student__user',
        'course'
    ).order_by(
        '-id'
    )[:5]


    # --------------------------------------------------------
    # RECENT RESULTS / MARKS
    # --------------------------------------------------------

    recent_results = Result.objects.select_related(
        'enrollment__student__user',
        'enrollment__course'
    ).order_by(
        '-id'
    )[:5]


    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {

        # Basic statistics
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'total_results': total_results,

        # Attendance
        'today_present': today_present,
        'today_absent': today_absent,
        'today_late': today_late,
        'today_leave': today_leave,
        'today_attendance_percentage': round(
            today_attendance_percentage,
            1
        ),

        # Recent data
        'recent_students': recent_students,
        'recent_enrollments': recent_enrollments,
        'recent_results': recent_results,

        # Date
        'today': today,
    }


    return render(
        request,
        'dashboard.html',
        context
    )


# ============================================================
# STUDENT LIST
# ============================================================

def student_list(request):

    students = Student.objects.select_related(
        'user'
    ).all().order_by(
        'student_id'
    )

    context = {
        'students': students,
    }

    return render(
        request,
        'students/student_list.html',
        context
    )


# ============================================================
# ADD STUDENT
# ============================================================

def student_create(request):

    if request.method == 'POST':

        username = request.POST.get(
            'username',
            ''
        ).strip()

        first_name = request.POST.get(
            'first_name',
            ''
        ).strip()

        last_name = request.POST.get(
            'last_name',
            ''
        ).strip()

        email = request.POST.get(
            'email',
            ''
        ).strip()

        password = request.POST.get(
            'password',
            ''
        )

        student_id = request.POST.get(
            'student_id',
            ''
        ).strip()

        phone = request.POST.get(
            'phone',
            ''
        ).strip()

        date_of_birth = request.POST.get(
            'date_of_birth'
        )

        gender = request.POST.get(
            'gender'
        )

        address = request.POST.get(
            'address',
            ''
        ).strip()

        department = request.POST.get(
            'department',
            ''
        ).strip()

        program = request.POST.get(
            'program',
            ''
        ).strip()

        semester = request.POST.get(
            'semester'
        )


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                'Username already exists.'
            )

            return redirect(
                'student_create'
            )


        if Student.objects.filter(
            student_id=student_id
        ).exists():

            messages.error(
                request,
                'Student ID already exists.'
            )

            return redirect(
                'student_create'
            )


        # ----------------------------------------------------
        # CREATE USER
        # ----------------------------------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='STUDENT'
        )


        # ----------------------------------------------------
        # CREATE STUDENT
        # ----------------------------------------------------

        student = Student.objects.create(

            user=user,

            student_id=student_id,

            phone=phone,

            date_of_birth=(
                date_of_birth
                if date_of_birth
                else None
            ),

            gender=gender,

            address=address,

            department=department,

            program=program,

            semester=semester,
        )


        messages.success(
            request,
            f'Student {student.student_id} added successfully.'
        )

        return redirect(
            'student_list'
        )


    return render(
        request,
        'students/student_form.html'
    )


# ============================================================
# UPDATE STUDENT
# ============================================================

def student_update(
    request,
    student_id
):

    student = get_object_or_404(
        Student.objects.select_related('user'),
        id=student_id
    )

    user = student.user


    if request.method == 'POST':

        user.first_name = request.POST.get(
            'first_name',
            ''
        ).strip()

        user.last_name = request.POST.get(
            'last_name',
            ''
        ).strip()

        user.email = request.POST.get(
            'email',
            ''
        ).strip()


        student.phone = request.POST.get(
            'phone',
            ''
        ).strip()

        date_of_birth = request.POST.get(
            'date_of_birth'
        )

        student.date_of_birth = (
            date_of_birth
            if date_of_birth
            else None
        )

        student.gender = request.POST.get(
            'gender'
        )

        student.address = request.POST.get(
            'address',
            ''
        ).strip()

        student.department = request.POST.get(
            'department',
            ''
        ).strip()

        student.program = request.POST.get(
            'program',
            ''
        ).strip()

        student.semester = request.POST.get(
            'semester'
        )


        user.save()

        student.save()


        messages.success(
            request,
            'Student updated successfully.'
        )

        return redirect(
            'student_list'
        )


    context = {
        'student': student,
    }

    return render(
        request,
        'students/student_form.html',
        context
    )


# ============================================================
# DELETE STUDENT
# ============================================================

def student_delete(
    request,
    student_id
):

    student = get_object_or_404(
        Student,
        id=student_id
    )


    if request.method == 'POST':

        student.delete()

        messages.success(
            request,
            'Student deleted successfully.'
        )

        return redirect(
            'student_list'
        )


    context = {
        'student': student,
    }

    return render(
        request,
        'students/student_confirm_delete.html',
        context
    )
# ============================================================
# STUDENT DASHBOARD
# ============================================================

def student_dashboard(request):

    # --------------------------------------------------------
    # GET LOGGED-IN STUDENT
    # --------------------------------------------------------

    student = get_object_or_404(
        Student.objects.select_related('user'),
        user=request.user
    )


    # --------------------------------------------------------
    # ENROLLMENTS
    # --------------------------------------------------------

    enrollments = Enrollment.objects.filter(
        student=student,
        is_active=True
    ).select_related(
        'course',
        'course__teacher__user'
    )


    total_courses = enrollments.count()


    # --------------------------------------------------------
    # OVERALL ATTENDANCE
    # --------------------------------------------------------

    attendance_records = Attendance.objects.filter(
        enrollment__student=student
    )


    total_attendance = attendance_records.count()

    present_count = attendance_records.filter(
        status='Present'
    ).count()

    late_count = attendance_records.filter(
        status='Late'
    ).count()

    absent_count = attendance_records.filter(
        status='Absent'
    ).count()

    leave_count = attendance_records.filter(
        status='Leave'
    ).count()


    if total_attendance > 0:

        attendance_percentage = (
            (present_count + late_count)
            / total_attendance
        ) * 100

    else:

        attendance_percentage = 0


    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    results = Result.objects.filter(
        enrollment__student=student
    ).select_related(
        'enrollment__course'
    ).order_by(
        '-created_at'
    )


    total_results = results.count()


    # --------------------------------------------------------
    # OVERALL ACADEMIC PERCENTAGE
    # --------------------------------------------------------

    total_obtained = 0
    total_possible = 0


    for result in results:

        total_obtained += result.obtained_marks
        total_possible += result.total_marks


    if total_possible > 0:

        overall_percentage = (
            total_obtained /
            total_possible
        ) * 100

    else:

        overall_percentage = 0


    # --------------------------------------------------------
    # COURSE DATA
    # --------------------------------------------------------
    # This prepares the data required by student_dashboard.html
    # --------------------------------------------------------

    course_data = []


    for enrollment in enrollments:

        course = enrollment.course


        # ----------------------------------------------------
        # Teacher
        # ----------------------------------------------------

        teacher = getattr(
            course,
            'teacher',
            None
        )


        # ----------------------------------------------------
        # Course Attendance
        # ----------------------------------------------------

        course_attendance = Attendance.objects.filter(
            enrollment=enrollment
        ).order_by(
            '-date'
        )


        course_total_attendance = course_attendance.count()


        course_present = course_attendance.filter(
            status='Present'
        ).count()


        course_late = course_attendance.filter(
            status='Late'
        ).count()


        if course_total_attendance > 0:

            course_attendance_percentage = (
                (course_present + course_late)
                / course_total_attendance
            ) * 100

        else:

            course_attendance_percentage = 0


        # ----------------------------------------------------
        # Course Results
        # ----------------------------------------------------

        course_results = Result.objects.filter(
            enrollment=enrollment
        ).order_by(
            '-created_at'
        )


        # ----------------------------------------------------
        # Add Course Information
        # ----------------------------------------------------

        course_data.append({

            'course': course,

            'teacher': teacher,

            'attendance_records': course_attendance,

            'attendance_percentage': round(
                course_attendance_percentage,
                2
            ),

            'results': course_results,

        })


    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {

        # Student
        'student': student,


        # Courses
        'enrollments': enrollments,
        'course_data': course_data,
        'total_courses': total_courses,


        # Overall attendance
        'total_attendance': total_attendance,
        'present_count': present_count,
        'late_count': late_count,
        'absent_count': absent_count,
        'leave_count': leave_count,

        'attendance_percentage': round(
            attendance_percentage,
            2
        ),


        # Results
        'results': results,
        'total_results': total_results,

        'total_obtained': total_obtained,
        'total_possible': total_possible,

        'overall_percentage': round(
            overall_percentage,
            2
        ),

    }


    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    return render(
        request,
        'students/student_dashboard.html',
        context
    )