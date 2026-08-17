from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect


# ============================================================
# ROLE REDIRECTION
# ============================================================

def redirect_user_by_role(request, user):

    # --------------------------------------------------------
    # ADMIN
    # --------------------------------------------------------

    if user.role == 'ADMIN':

        return redirect(
            'dashboard'
        )


    # --------------------------------------------------------
    # TEACHER
    # --------------------------------------------------------

    elif user.role == 'TEACHER':

        if hasattr(user, 'teacher_profile'):

            return redirect(
                'teacher_dashboard',
                teacher_id=user.teacher_profile.id
            )

        logout(request)

        messages.error(
            request,
            'No teacher profile is associated with this account.'
        )

        return redirect(
            'login'
        )


    # --------------------------------------------------------
    # STUDENT
    # --------------------------------------------------------

    elif user.role == 'STUDENT':

        if hasattr(user, 'student_profile'):

            return redirect(
                'student_dashboard'
            )

        logout(request)

        messages.error(
            request,
            'No student profile is associated with this account.'
        )

        return redirect(
            'login'
        )


    # --------------------------------------------------------
    # INVALID ROLE
    # --------------------------------------------------------

    else:

        logout(request)

        messages.error(
            request,
            'Your account does not have a valid role.'
        )

        return redirect(
            'login'
        )


# ============================================================
# LOGIN
# ============================================================

def login_view(request):

    # --------------------------------------------------------
    # Already logged in
    # --------------------------------------------------------

    if request.user.is_authenticated:

        return redirect_user_by_role(
            request,
            request.user
        )


    # --------------------------------------------------------
    # Login form submitted
    # --------------------------------------------------------

    if request.method == 'POST':

        username = request.POST.get(
            'username',
            ''
        ).strip()

        password = request.POST.get(
            'password',
            ''
        )


        # ----------------------------------------------------
        # Validate input
        # ----------------------------------------------------

        if not username or not password:

            messages.error(
                request,
                'Please enter both username and password.'
            )

            return render(
                request,
                'accounts/login.html'
            )


        # ----------------------------------------------------
        # Authenticate user
        # ----------------------------------------------------

        user = authenticate(
            request,
            username=username,
            password=password
        )


        # ----------------------------------------------------
        # Invalid credentials
        # ----------------------------------------------------

        if user is None:

            messages.error(
                request,
                'Invalid username or password.'
            )

            return render(
                request,
                'accounts/login.html'
            )


        # ----------------------------------------------------
        # Login user
        # ----------------------------------------------------

        login(
            request,
            user
        )


        # ----------------------------------------------------
        # Redirect according to role
        # ----------------------------------------------------

        return redirect_user_by_role(
            request,
            user
        )


    # --------------------------------------------------------
    # Display login page
    # --------------------------------------------------------

    return render(
        request,
        'accounts/login.html'
    )


# ============================================================
# LOGOUT
# ============================================================

def logout_view(request):

    logout(request)

    messages.success(
        request,
        'You have been logged out successfully.'
    )

    return redirect(
        'login'
    )