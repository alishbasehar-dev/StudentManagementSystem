from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.db import IntegrityError
from django.utils.dateparse import parse_date

from .models import (
    Course,
    Enrollment,
    Attendance,
    Result,
)

from .forms import (
    CourseForm,
    EnrollmentForm,
    ResultForm,
)

from students.models import Student


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def is_admin(user):
    """
    User is considered an administrator if:
    1. They have role = ADMIN
    OR
    2. They are a Django superuser.
    """

    return (
        user.is_authenticated
        and (
            getattr(user, 'role', None) == 'ADMIN'
            or user.is_superuser
        )
    )


def is_teacher(user):

    return (
        user.is_authenticated
        and getattr(user, 'role', None) == 'TEACHER'
    )


def is_student(user):

    return (
        user.is_authenticated
        and getattr(user, 'role', None) == 'STUDENT'
    )


# ============================================================
# COURSE LIST
# ============================================================

def course_list(request):

    if not request.user.is_authenticated:
        return redirect('login')

    courses = Course.objects.select_related(
        'teacher',
        'teacher__user'
    ).order_by(
        'course_code'
    )

    context = {
        'courses': courses,
    }

    return render(
        request,
        'courses/course_list.html',
        context
    )


# ============================================================
# CREATE COURSE
# ============================================================

def course_create(request):

    if not is_admin(request.user):

        messages.error(
            request,
            'Only administrators can create courses.'
        )

        return redirect_user_dashboard(request)

    if request.method == 'POST':

        form = CourseForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Course created successfully.'
            )

            return redirect(
                'course_list'
            )

    else:

        form = CourseForm()

    context = {
        'form': form,
        'page_title': 'Add Course',
    }

    return render(
        request,
        'courses/course_form.html',
        context
    )


# ============================================================
# UPDATE COURSE
# ============================================================

def course_update(
    request,
    course_id
):

    if not is_admin(request.user):

        messages.error(
            request,
            'Only administrators can update courses.'
        )

        return redirect_user_dashboard(request)

    course = get_object_or_404(
        Course,
        id=course_id
    )

    if request.method == 'POST':

        form = CourseForm(
            request.POST,
            instance=course
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Course updated successfully.'
            )

            return redirect(
                'course_list'
            )

    else:

        form = CourseForm(
            instance=course
        )

    context = {
        'form': form,
        'course': course,
        'page_title': 'Edit Course',
    }

    return render(
        request,
        'courses/course_form.html',
        context
    )


# ============================================================
# DELETE COURSE
# ============================================================

def course_delete(
    request,
    course_id
):

    if not is_admin(request.user):

        messages.error(
            request,
            'Only administrators can delete courses.'
        )

        return redirect_user_dashboard(request)

    course = get_object_or_404(
        Course,
        id=course_id
    )

    if request.method == 'POST':

        course.delete()

        messages.success(
            request,
            'Course deleted successfully.'
        )

        return redirect(
            'course_list'
        )

    context = {
        'course': course,
    }

    return render(
        request,
        'courses/course_confirm_delete.html',
        context
    )


# ============================================================
# ENROLLMENT LIST
# ============================================================

def enrollment_list(request):

    if not is_admin(request.user):

        messages.error(
            request,
            'Only administrators can manage enrollments.'
        )

        return redirect_user_dashboard(request)

    enrollments = Enrollment.objects.select_related(
        'student__user',
        'course',
        'course__teacher',
        'course__teacher__user'
    ).order_by(
        '-enrollment_date'
    )

    context = {
        'enrollments': enrollments,
    }

    return render(
        request,
        'courses/enrollment_list.html',
        context
    )


# ============================================================
# CREATE ENROLLMENT
# ============================================================

def enrollment_create(request):

    if not is_admin(request.user):

        messages.error(
            request,
            'Only administrators can enroll students.'
        )

        return redirect_user_dashboard(request)

    if request.method == 'POST':

        form = EnrollmentForm(
            request.POST
        )

        if form.is_valid():

            try:

                form.save()

                messages.success(
                    request,
                    'Student enrolled successfully.'
                )

                return redirect(
                    'enrollment_list'
                )

            except IntegrityError:

                messages.error(
                    request,
                    'This student is already enrolled in this course.'
                )

    else:

        form = EnrollmentForm()

    context = {
        'form': form,
        'page_title': 'Enroll Student',
    }

    return render(
        request,
        'courses/enrollment_form.html',
        context
    )


# ============================================================
# DELETE ENROLLMENT
# ============================================================

def enrollment_delete(
    request,
    enrollment_id
):

    if not is_admin(request.user):

        messages.error(
            request,
            'Only administrators can remove enrollments.'
        )

        return redirect_user_dashboard(request)

    enrollment = get_object_or_404(
        Enrollment,
        id=enrollment_id
    )

    if request.method == 'POST':

        enrollment.delete()

        messages.success(
            request,
            'Enrollment removed successfully.'
        )

        return redirect(
            'enrollment_list'
        )

    context = {
        'enrollment': enrollment,
    }

    return render(
        request,
        'courses/enrollment_confirm_delete.html',
        context
    )


# ============================================================
# ATTENDANCE
# ============================================================

def attendance(
    request,
    course_id
):

    if not request.user.is_authenticated:
        return redirect('login')

    course = get_object_or_404(
        Course.objects.select_related(
            'teacher',
            'teacher__user'
        ),
        id=course_id
    )

    # --------------------------------------------------------
    # ADMIN
    # --------------------------------------------------------

    if is_admin(request.user):

        pass

    # --------------------------------------------------------
    # TEACHER
    # --------------------------------------------------------

    elif is_teacher(request.user):

        if not hasattr(
            request.user,
            'teacher_profile'
        ):

            messages.error(
                request,
                'No teacher profile is associated with your account.'
            )

            return redirect('login')

        if (
            not course.teacher
            or course.teacher.user != request.user
        ):

            messages.error(
                request,
                'You are not authorized to manage attendance for this course.'
            )

            return redirect(
                'teacher_dashboard',
                teacher_id=request.user.teacher_profile.id
            )

    # --------------------------------------------------------
    # OTHER USERS
    # --------------------------------------------------------

    else:

        messages.error(
            request,
            'You are not authorized to manage attendance.'
        )

        return redirect_user_dashboard(request)

    enrollments = Enrollment.objects.filter(
        course=course,
        is_active=True
    ).select_related(
        'student__user'
    ).order_by(
        'student__student_id'
    )

    if request.method == 'POST':

        attendance_date = request.POST.get(
            'date'
        )

        parsed_date = parse_date(
            attendance_date
        )

        if not parsed_date:

            messages.error(
                request,
                'Please select a valid attendance date.'
            )

            return redirect(
                'attendance',
                course_id=course.id
            )

        valid_statuses = {
            'Present',
            'Absent',
            'Late',
            'Leave',
        }

        for enrollment in enrollments:

            status = request.POST.get(
                f'attendance_{enrollment.id}'
            )

            remarks = request.POST.get(
                f'remarks_{enrollment.id}',
                ''
            ).strip()

            if status not in valid_statuses:
                continue

            Attendance.objects.update_or_create(

                enrollment=enrollment,

                date=parsed_date,

                defaults={
                    'status': status,
                    'remarks': remarks,
                }
            )

        messages.success(
            request,
            'Attendance saved successfully.'
        )

        return redirect(
            'attendance',
            course_id=course.id
        )

    context = {
        'course': course,
        'enrollments': enrollments,
    }

    return render(
        request,
        'courses/attendance.html',
        context
    )


# ============================================================
# STUDENT ACADEMIC RECORD
# ============================================================

def student_academic_record(
    request,
    student_id
):

    if not request.user.is_authenticated:
        return redirect('login')

    student = get_object_or_404(
        Student.objects.select_related('user'),
        id=student_id
    )

    # --------------------------------------------------------
    # STUDENT
    # --------------------------------------------------------

    if is_student(request.user):

        if student.user != request.user:

            messages.error(
                request,
                'You are not authorized to view this academic record.'
            )

            return redirect(
                'student_dashboard'
            )

    # --------------------------------------------------------
    # TEACHER
    # --------------------------------------------------------

    elif is_teacher(request.user):

        if not hasattr(
            request.user,
            'teacher_profile'
        ):

            messages.error(
                request,
                'No teacher profile is associated with your account.'
            )

            return redirect('login')

        teacher = request.user.teacher_profile

        has_teacher_course = Enrollment.objects.filter(
            student=student,
            course__teacher=teacher,
            is_active=True
        ).exists()

        if not has_teacher_course:

            messages.error(
                request,
                'You are not authorized to view this student record.'
            )

            return redirect(
                'teacher_dashboard',
                teacher_id=teacher.id
            )

    # --------------------------------------------------------
    # ADMIN
    # --------------------------------------------------------

    elif is_admin(request.user):

        pass

    # --------------------------------------------------------
    # OTHER
    # --------------------------------------------------------

    else:

        messages.error(
            request,
            'You are not authorized to view academic records.'
        )

        return redirect('login')

    enrollments = Enrollment.objects.filter(
        student=student,
        is_active=True
    ).select_related(
        'course',
        'course__teacher',
        'course__teacher__user'
    ).order_by(
        'course__course_code'
    )

    academic_records = []

    for enrollment in enrollments:

        # ====================================================
        # ATTENDANCE
        # ====================================================

        attendance_records = (
            enrollment.attendance_records.all()
        )

        total_attendance = (
            attendance_records.count()
        )

        present_count = (
            attendance_records
            .filter(status='Present')
            .count()
        )

        absent_count = (
            attendance_records
            .filter(status='Absent')
            .count()
        )

        late_count = (
            attendance_records
            .filter(status='Late')
            .count()
        )

        leave_count = (
            attendance_records
            .filter(status='Leave')
            .count()
        )

        if total_attendance > 0:

            attendance_percentage = (
                (
                    present_count +
                    late_count
                )
                / total_attendance
            ) * 100

        else:

            attendance_percentage = 0

        # ====================================================
        # RESULTS
        # ====================================================

        results = (
            enrollment.results
            .all()
            .order_by('-created_at')
        )

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

        academic_records.append({

            'enrollment': enrollment,

            'course': enrollment.course,

            'attendance_records': attendance_records,

            'total_attendance': total_attendance,

            'present_count': present_count,

            'absent_count': absent_count,

            'late_count': late_count,

            'leave_count': leave_count,

            'attendance_percentage': round(
                attendance_percentage,
                2
            ),

            'results': results,

            'total_obtained': total_obtained,

            'total_possible': total_possible,

            'overall_percentage': round(
                overall_percentage,
                2
            ),
        })

    context = {
        'student': student,
        'academic_records': academic_records,
    }

    return render(
        request,
        'courses/student_academic_record.html',
        context
    )


# ============================================================
# RESULT / MARKS LIST
# ============================================================

def result_list(request):

    if not request.user.is_authenticated:
        return redirect('login')

    # --------------------------------------------------------
    # ADMIN
    # --------------------------------------------------------

    if is_admin(request.user):

        results = Result.objects.select_related(
            'enrollment__student__user',
            'enrollment__course'
        ).order_by(
            '-created_at'
        )

    # --------------------------------------------------------
    # TEACHER
    # --------------------------------------------------------

    elif is_teacher(request.user):

        if not hasattr(
            request.user,
            'teacher_profile'
        ):

            messages.error(
                request,
                'No teacher profile is associated with your account.'
            )

            return redirect('login')

        teacher = request.user.teacher_profile

        results = Result.objects.filter(
            enrollment__course__teacher=teacher
        ).select_related(
            'enrollment__student__user',
            'enrollment__course'
        ).order_by(
            '-created_at'
        )

    # --------------------------------------------------------
    # STUDENT
    # --------------------------------------------------------

    elif is_student(request.user):

        results = Result.objects.filter(
            enrollment__student__user=request.user
        ).select_related(
            'enrollment__student__user',
            'enrollment__course'
        ).order_by(
            '-created_at'
        )

    else:

        messages.error(
            request,
            'You are not authorized to view results.'
        )

        return redirect('login')

    context = {
        'results': results,
    }

    return render(
        request,
        'courses/result_list.html',
        context
    )


# ============================================================
# ADD RESULT / MARKS
# ============================================================

def result_create(request):

    if not request.user.is_authenticated:
        return redirect('login')

    if not (
        is_admin(request.user)
        or is_teacher(request.user)
    ):

        messages.error(
            request,
            'Only administrators and teachers can enter marks.'
        )

        return redirect_user_dashboard(request)

    if request.method == 'POST':

        form = ResultForm(
            request.POST
        )

        if form.is_valid():

            result = form.save(
                commit=False
            )

            if is_teacher(request.user):

                if not hasattr(
                    request.user,
                    'teacher_profile'
                ):

                    messages.error(
                        request,
                        'No teacher profile is associated with your account.'
                    )

                    return redirect('login')

                teacher = request.user.teacher_profile

                if result.enrollment.course.teacher != teacher:

                    messages.error(
                        request,
                        'You can only enter marks for your own courses.'
                    )

                    return redirect(
                        'teacher_dashboard',
                        teacher_id=teacher.id
                    )

            result.save()

            messages.success(
                request,
                'Marks entered successfully.'
            )

            return redirect(
                'result_list'
            )

    else:

        form = ResultForm()

    context = {
        'form': form,
        'page_title': 'Enter Marks',
    }

    return render(
        request,
        'courses/result_form.html',
        context
    )


# ============================================================
# EDIT RESULT / MARKS
# ============================================================

def result_update(
    request,
    result_id
):

    if not request.user.is_authenticated:
        return redirect('login')

    result = get_object_or_404(
        Result.objects.select_related(
            'enrollment__course__teacher'
        ),
        id=result_id
    )

    # --------------------------------------------------------
    # TEACHER
    # --------------------------------------------------------

    if is_teacher(request.user):

        if not hasattr(
            request.user,
            'teacher_profile'
        ):

            messages.error(
                request,
                'No teacher profile is associated with your account.'
            )

            return redirect('login')

        teacher = request.user.teacher_profile

        if result.enrollment.course.teacher != teacher:

            messages.error(
                request,
                'You can only edit marks for your own courses.'
            )

            return redirect(
                'teacher_dashboard',
                teacher_id=teacher.id
            )

    # --------------------------------------------------------
    # ADMIN
    # --------------------------------------------------------

    elif is_admin(request.user):

        pass

    # --------------------------------------------------------
    # OTHER
    # --------------------------------------------------------

    else:

        messages.error(
            request,
            'You are not authorized to edit marks.'
        )

        return redirect_user_dashboard(request)

    if request.method == 'POST':

        form = ResultForm(
            request.POST,
            instance=result
        )

        if form.is_valid():

            updated_result = form.save(
                commit=False
            )

            if is_teacher(request.user):

                teacher = request.user.teacher_profile

                if (
                    updated_result
                    .enrollment
                    .course
                    .teacher != teacher
                ):

                    messages.error(
                        request,
                        'You can only edit marks for your own courses.'
                    )

                    return redirect(
                        'teacher_dashboard',
                        teacher_id=teacher.id
                    )

            updated_result.save()

            messages.success(
                request,
                'Marks updated successfully.'
            )

            return redirect(
                'result_list'
            )

    else:

        form = ResultForm(
            instance=result
        )

    context = {
        'form': form,
        'result': result,
        'page_title': 'Edit Marks',
    }

    return render(
        request,
        'courses/result_form.html',
        context
    )


# ============================================================
# DELETE RESULT
# ============================================================

def result_delete(
    request,
    result_id
):

    if not request.user.is_authenticated:
        return redirect('login')

    result = get_object_or_404(
        Result.objects.select_related(
            'enrollment__course__teacher'
        ),
        id=result_id
    )

    # --------------------------------------------------------
    # TEACHER
    # --------------------------------------------------------

    if is_teacher(request.user):

        if not hasattr(
            request.user,
            'teacher_profile'
        ):

            messages.error(
                request,
                'No teacher profile is associated with your account.'
            )

            return redirect('login')

        teacher = request.user.teacher_profile

        if result.enrollment.course.teacher != teacher:

            messages.error(
                request,
                'You can only delete marks for your own courses.'
            )

            return redirect(
                'teacher_dashboard',
                teacher_id=teacher.id
            )

    # --------------------------------------------------------
    # ADMIN
    # --------------------------------------------------------

    elif is_admin(request.user):

        pass

    # --------------------------------------------------------
    # OTHER
    # --------------------------------------------------------

    else:

        messages.error(
            request,
            'You are not authorized to delete marks.'
        )

        return redirect_user_dashboard(request)

    if request.method == 'POST':

        result.delete()

        messages.success(
            request,
            'Result deleted successfully.'
        )

        return redirect(
            'result_list'
        )

    context = {
        'result': result,
    }

    return render(
        request,
        'courses/result_confirm_delete.html',
        context
    )


# ============================================================
# DASHBOARD REDIRECTION HELPER
# ============================================================

def redirect_user_dashboard(request):

    if not request.user.is_authenticated:
        return redirect('login')

    # --------------------------------------------------------
    # ADMIN
    # --------------------------------------------------------

    if is_admin(request.user):

        return redirect(
            'dashboard'
        )

    # --------------------------------------------------------
    # TEACHER
    # --------------------------------------------------------

    if is_teacher(request.user):

        if hasattr(
            request.user,
            'teacher_profile'
        ):

            return redirect(
                'teacher_dashboard',
                teacher_id=request.user.teacher_profile.id
            )

        return redirect('login')

    # --------------------------------------------------------
    # STUDENT
    # --------------------------------------------------------

    if is_student(request.user):

        return redirect(
            'student_dashboard'
        )

    return redirect('login')