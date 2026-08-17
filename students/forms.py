from django import forms
from .models import Student


class StudentForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = [
            'user',
            'student_id',
            'phone',
            'date_of_birth',
            'gender',
            'address',
            'department',
            'program',
            'semester',
            'profile_picture',
        ]

        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={'type': 'date'}
            ),

            'address': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Enter student address'
                }
            ),

            'student_id': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. STU001'
                }
            ),

            'phone': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. 03001234567'
                }
            ),

            'department': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. Electronics'
                }
            ),

            'program': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. BS Electronics and Computing'
                }
            ),

            'semester': forms.NumberInput(
                attrs={
                    'min': 1,
                    'max': 8
                }
            ),
        }