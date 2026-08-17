from django import forms
from django.db import transaction

from accounts.models import User
from .models import Teacher


# ============================================================
# TEACHER FORM
# ============================================================

class TeacherForm(forms.ModelForm):

    # ========================================================
    # USER ACCOUNT FIELDS
    # ========================================================

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter username',
            }
        )
    )

    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name',
            }
        )
    )

    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name',
            }
        )
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address',
            }
        )
    )

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter password',
            }
        )
    )


    # ========================================================
    # MODEL CONFIGURATION
    # ========================================================

    class Meta:

        model = Teacher

        fields = [
            'teacher_id',
            'department',
            'qualification',
            'phone',
            'designation',
            'joining_date',
            'is_active',
        ]

        widgets = {

            'teacher_id': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g. TCH001',
                }
            ),

            'department': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g. Electronics',
                }
            ),

            'qualification': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g. MS Electronics',
                }
            ),

            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g. 03001234567',
                }
            ),

            'designation': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g. Lecturer',
                }
            ),

            'joining_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),

            'is_active': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
        }


    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # ----------------------------------------------------
        # EDITING EXISTING TEACHER
        # ----------------------------------------------------

        if self.instance and self.instance.pk:

            user = self.instance.user

            self.fields['username'].initial = (
                user.username
            )

            self.fields['first_name'].initial = (
                user.first_name
            )

            self.fields['last_name'].initial = (
                user.last_name
            )

            self.fields['email'].initial = (
                user.email
            )

            self.fields['password'].help_text = (
                'Leave blank to keep the current password.'
            )

        # ----------------------------------------------------
        # CREATING NEW TEACHER
        # ----------------------------------------------------

        else:

            self.fields['password'].required = True

            self.fields['password'].help_text = (
                'Password is required for a new teacher account.'
            )


    # ========================================================
    # USERNAME VALIDATION
    # ========================================================

    def clean_username(self):

        username = self.cleaned_data.get(
            'username'
        )

        if not username:
            raise forms.ValidationError(
                'Username is required.'
            )

        users = User.objects.filter(
            username=username
        )

        # ----------------------------------------------------
        # When editing, ignore the current teacher's user
        # ----------------------------------------------------

        if self.instance and self.instance.pk:

            users = users.exclude(
                pk=self.instance.user.pk
            )

        if users.exists():

            raise forms.ValidationError(
                'This username is already in use.'
            )

        return username


    # ========================================================
    # EMAIL VALIDATION
    # ========================================================

    def clean_email(self):

        email = self.cleaned_data.get(
            'email'
        )

        if not email:
            raise forms.ValidationError(
                'Email address is required.'
            )

        users = User.objects.filter(
            email=email
        )

        # ----------------------------------------------------
        # When editing, ignore current teacher's account
        # ----------------------------------------------------

        if self.instance and self.instance.pk:

            users = users.exclude(
                pk=self.instance.user.pk
            )

        if users.exists():

            raise forms.ValidationError(
                'This email address is already in use.'
            )

        return email


    # ========================================================
    # SAVE TEACHER + USER
    # ========================================================

    @transaction.atomic
    def save(self, commit=True):

        teacher = super().save(
            commit=False
        )

        # ====================================================
        # EXISTING TEACHER
        # ====================================================

        if teacher.pk:

            user = teacher.user

            user.username = (
                self.cleaned_data['username']
            )

            user.first_name = (
                self.cleaned_data['first_name']
            )

            user.last_name = (
                self.cleaned_data['last_name']
            )

            user.email = (
                self.cleaned_data['email']
            )

            user.role = 'TEACHER'

            password = self.cleaned_data.get(
                'password'
            )

            if password:

                user.set_password(
                    password
                )

            if commit:

                user.save()

                teacher.save()

            return teacher


        # ====================================================
        # NEW TEACHER
        # ====================================================

        user = User.objects.create_user(

            username=self.cleaned_data[
                'username'
            ],

            email=self.cleaned_data[
                'email'
            ],

            password=self.cleaned_data[
                'password'
            ],

            first_name=self.cleaned_data[
                'first_name'
            ],

            last_name=self.cleaned_data[
                'last_name'
            ],

            role='TEACHER',
        )


        # Connect User with Teacher

        teacher.user = user


        # Save Teacher

        if commit:

            teacher.save()


        return teacher