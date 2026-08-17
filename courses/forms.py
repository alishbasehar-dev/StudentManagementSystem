from django import forms

from .models import (
    Course,
    Enrollment,
    Result,
)

from teachers.models import Teacher


# ============================================================
# COURSE FORM
# ============================================================

class CourseForm(forms.ModelForm):

    class Meta:

        model = Course

        fields = [
            'course_code',
            'course_name',
            'description',
            'credit_hours',
            'semester',
            'department',
            'teacher',
            'is_active',
        ]

        widgets = {

            'course_code': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g. CS101',
                }
            ),

            'course_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Course name',
                }
            ),

            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Course description',
                }
            ),

            'credit_hours': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 1,
                }
            ),

            'semester': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 1,
                }
            ),

            'department': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Department',
                }
            ),

            'teacher': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            'is_active': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
        }


# ============================================================
# ENROLLMENT FORM
# ============================================================

class EnrollmentForm(forms.ModelForm):

    class Meta:

        model = Enrollment

        fields = [
            'student',
            'course',
            'is_active',
        ]

        widgets = {

            'student': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            'course': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            'is_active': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
        }


# ============================================================
# RESULT / MARKS FORM
# ============================================================

class ResultForm(forms.ModelForm):

    EXAM_TYPE_CHOICES = [

        ('Assignment', 'Assignment'),

        ('Quiz', 'Quiz'),

        ('Midterm', 'Midterm'),

        ('Final', 'Final'),

        ('Other', 'Other'),

    ]

    exam_type = forms.ChoiceField(

        choices=EXAM_TYPE_CHOICES,

        widget=forms.Select(
            attrs={
                'class': 'form-select',
            }
        )

    )


    class Meta:

        model = Result

        fields = [

            'enrollment',

            'exam_type',

            'exam_name',

            'obtained_marks',

            'total_marks',

            'remarks',

        ]

        widgets = {

            'enrollment': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            'exam_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g. Midterm Exam',
                }
            ),

            'obtained_marks': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': 'Obtained marks',
                }
            ),

            'total_marks': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0.01',
                    'placeholder': 'Total marks',
                }
            ),

            'remarks': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Optional remarks',
                }
            ),
        }


    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        *args,
        user=None,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )


        # ----------------------------------------------------
        # TEACHER
        # ----------------------------------------------------

        if (
            user
            and getattr(user, 'role', None)
            == 'TEACHER'
        ):

            try:

                teacher = Teacher.objects.get(
                    user=user
                )

                self.fields[
                    'enrollment'
                ].queryset = Enrollment.objects.filter(

                    course__teacher=teacher,

                    is_active=True

                ).select_related(

                    'student__user',

                    'course'

                ).order_by(

                    'course__course_code',

                    'student__student_id'

                )

            except Teacher.DoesNotExist:

                self.fields[
                    'enrollment'
                ].queryset = Enrollment.objects.none()


        # ----------------------------------------------------
        # ADMIN
        # ----------------------------------------------------

        else:

            self.fields[
                'enrollment'
            ].queryset = Enrollment.objects.filter(

                is_active=True

            ).select_related(

                'student__user',

                'course'

            ).order_by(

                'course__course_code',

                'student__student_id'

            )


    # ========================================================
    # VALIDATION
    # ========================================================

    def clean(self):

        cleaned_data = super().clean()

        obtained = cleaned_data.get(
            'obtained_marks'
        )

        total = cleaned_data.get(
            'total_marks'
        )


        # ----------------------------------------------------
        # NEGATIVE MARKS
        # ----------------------------------------------------

        if (
            obtained is not None
            and obtained < 0
        ):

            self.add_error(

                'obtained_marks',

                'Obtained marks cannot be negative.'

            )


        # ----------------------------------------------------
        # TOTAL MARKS
        # ----------------------------------------------------

        if (
            total is not None
            and total <= 0
        ):

            self.add_error(

                'total_marks',

                'Total marks must be greater than zero.'

            )


        # ----------------------------------------------------
        # OBTAINED > TOTAL
        # ----------------------------------------------------

        if (
            obtained is not None
            and total is not None
            and obtained > total
        ):

            self.add_error(

                'obtained_marks',

                'Obtained marks cannot be greater than total marks.'

            )


        return cleaned_data
