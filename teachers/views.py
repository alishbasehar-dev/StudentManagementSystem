from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .models import Teacher
from .forms import TeacherForm

from courses.models import (
    Course,
    Enrollment,
    Attendance,
    Result,
)


# ============================================================
# ADMIN CHECK
# ============================================================

def is_admin_user(user):
    """
    Allow both Django superusers and users whose custom
    role is ADMIN.
    """

    return (
        user.is_superuser
        or getattr(user, 'role', '').upper() == 'ADMIN'
    )


# ============================================================
# TEACHER LIST
# ============================================================

@login_required
def teacher_list(request):

    if not is_admin_user(request.user):

        messages.error(
            request,
            'Only administrators can view teacher management.'
        )

        return redirect('dashboard')

    teachers = Teacher.objects.select_related(
        'user'
    ).order_by(
        'teacher_id'
    )

    context = {
        'teachers': teachers,
    }

    return render(
        request,
        'teachers/teacher_list.html',
        context
    )


# ============================================================
# ADD TEACHER
# ============================================================

@login_required
def teacher_create(request):

    if not is_admin_user(request.user):

        messages.error(
            request,
            'Only administrators can add teachers.'
        )

        return redirect('dashboard')

    if request.method == 'POST':

        form = TeacherForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Teacher created successfully.'
            )

            return redirect(
                'teacher_list'
            )

    else:

        form = TeacherForm()

    context = {
        'form': form,
        'page_title': 'Add Teacher',
    }

    return render(
        request,
        'teachers/teacher_form.html',
        context
    )


# ============================================================
# EDIT TEACHER
# ============================================================

@login_required
def teacher_update(
    request,
    teacher_id
):

    if not is_admin_user(request.user):

        messages.error(
            request,
            'Only administrators can edit teachers.'
        )

        return redirect('dashboard')

    teacher = get_object_or_404(
        Teacher,
        id=teacher_id
    )

    if request.method == 'POST':

        form = TeacherForm(
            request.POST,
            instance=teacher
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Teacher updated successfully.'
            )

            return redirect(
                'teacher_list'
            )

    else:

        form = TeacherForm(
            instance=teacher
        )

    context = {
        'form': form,
        'teacher': teacher,
        'page_title': 'Edit Teacher',
    }

    return render(
        request,
        'teachers/teacher_form.html',
        context
    )


# ============================================================
# DELETE TEACHER
# ============================================================

@login_required
def teacher_delete(
    request,
    teacher_id
):

    if not is_admin_user(request.user):

        messages.error(
            request,
            'Only administrators can delete teachers.'
        )

        return redirect('dashboard')

    teacher = get_object_or_404(
        Teacher,
        id=teacher_id
    )

    if request.method == 'POST':

        teacher.delete()

        messages.success(
            request,
            'Teacher deleted successfully.'
        )

        return redirect(
            'teacher_list'
        )

    context = {
        'teacher': teacher,
    }

    return render(
        request,
        'teachers/teacher_confirm_delete.html',
        context
    )


# ============================================================
# TEACHER DASHBOARD
# ============================================================

@login_required
def teacher_dashboard(
    request,
    teacher_id
):

    teacher = get_object_or_404(
        Teacher.objects.select_related(
            'user'
        ),
        id=teacher_id
    )

    # ========================================================
    # SECURITY
    # ========================================================

    if is_admin_user(request.user):

        # Admin can view any teacher dashboard
        pass

    elif getattr(request.user, 'role', '').upper() == 'TEACHER':

        if not hasattr(
            request.user,
            'teacher_profile'
        ):

            messages.error(
                request,
                'No teacher profile is associated with your account.'
            )

            return redirect('login')

        if request.user.teacher_profile.id != teacher.id:

            messages.error(
                request,
                'You are not authorized to view this teacher dashboard.'
            )

            return redirect(
                'teacher_dashboard',
                teacher_id=request.user.teacher_profile.id
            )

    else:

        messages.error(
            request,
            'You are not authorized to access the teacher dashboard.'
        )

        return redirect('login')


    # ========================================================
    # COURSES ASSIGNED TO TEACHER
    # ========================================================

    courses = teacher.courses.all().order_by(
        'course_code'
    )


    # ========================================================
    # INITIAL TOTALS
    # ========================================================

    course_data = []

    total_students = 0

    total_attendance = 0
    total_present = 0
    total_absent = 0
    total_late = 0
    total_leave = 0

    total_results = 0

    total_obtained_marks = 0
    total_possible_marks = 0


    # ========================================================
    # PROCESS COURSES
    # ========================================================

    for course in courses:

        # ----------------------------------------------------
        # ENROLLMENTS
        # ----------------------------------------------------

        enrollments = Enrollment.objects.filter(
            course=course,
            is_active=True
        ).select_related(
            'student__user'
        )

        student_count = enrollments.count()

        total_students += student_count


        # ----------------------------------------------------
        # ATTENDANCE
        # ----------------------------------------------------

        attendance_records = Attendance.objects.filter(
            enrollment__course=course,
            enrollment__is_active=True
        ).order_by(
            '-date'
        )

        attendance_total = attendance_records.count()

        present_count = attendance_records.filter(
            status='Present'
        ).count()

        absent_count = attendance_records.filter(
            status='Absent'
        ).count()

        late_count = attendance_records.filter(
            status='Late'
        ).count()

        leave_count = attendance_records.filter(
            status='Leave'
        ).count()


        # ----------------------------------------------------
        # ATTENDANCE PERCENTAGE
        # ----------------------------------------------------

        if attendance_total > 0:

            course_attendance_percentage = (
                (
                    present_count +
                    late_count
                )
                /
                attendance_total
            ) * 100

        else:

            course_attendance_percentage = 0


        # ----------------------------------------------------
        # OVERALL ATTENDANCE TOTALS
        # ----------------------------------------------------

        total_attendance += attendance_total

        total_present += present_count

        total_absent += absent_count

        total_late += late_count

        total_leave += leave_count


        # ----------------------------------------------------
        # RESULTS
        # ----------------------------------------------------

        results = Result.objects.filter(
            enrollment__course=course,
            enrollment__is_active=True
        ).select_related(
            'enrollment__student__user'
        ).order_by(
            '-created_at'
        )

        course_results_count = results.count()

        total_results += course_results_count


        # ----------------------------------------------------
        # COURSE MARKS
        # ----------------------------------------------------

        course_obtained_marks = 0

        course_possible_marks = 0

        for result in results:

            course_obtained_marks += result.obtained_marks

            course_possible_marks += result.total_marks


        total_obtained_marks += course_obtained_marks

        total_possible_marks += course_possible_marks


        # ----------------------------------------------------
        # COURSE PERCENTAGE
        # ----------------------------------------------------

        if course_possible_marks > 0:

            course_percentage = (
                course_obtained_marks /
                course_possible_marks
            ) * 100

        else:

            course_percentage = 0


        # ----------------------------------------------------
        # COURSE DATA
        # ----------------------------------------------------

        course_data.append({

            'course': course,

            'enrollments': enrollments,

            'student_count': student_count,

            'attendance_records': attendance_records,

            'attendance_total': attendance_total,

            'present_count': present_count,

            'absent_count': absent_count,

            'late_count': late_count,

            'leave_count': leave_count,

            'attendance_percentage': round(
                course_attendance_percentage,
                2
            ),

            'results': results,

            'total_results': course_results_count,

            'obtained_marks': course_obtained_marks,

            'possible_marks': course_possible_marks,

            'percentage': round(
                course_percentage,
                2
            ),
        })


    # ========================================================
    # OVERALL ATTENDANCE
    # ========================================================

    if total_attendance > 0:

        overall_attendance = (
            (
                total_present +
                total_late
            )
            /
            total_attendance
        ) * 100

    else:

        overall_attendance = 0


    # ========================================================
    # OVERALL ACADEMIC PERCENTAGE
    # ========================================================

    if total_possible_marks > 0:

        overall_percentage = (
            total_obtained_marks /
            total_possible_marks
        ) * 100

    else:

        overall_percentage = 0


    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        'teacher': teacher,

        'course_data': course_data,

        'total_courses': courses.count(),

        'total_students': total_students,

        'total_attendance': total_attendance,

        'total_present': total_present,

        'total_absent': total_absent,

        'total_late': total_late,

        'total_leave': total_leave,

        'overall_attendance': round(
            overall_attendance,
            2
        ),

        'total_results': total_results,

        'total_obtained_marks': total_obtained_marks,

        'total_possible_marks': total_possible_marks,

        'overall_percentage': round(
            overall_percentage,
            2
        ),
    }


    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        'teachers/dashboard.html',
        context
    )