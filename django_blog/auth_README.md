Authentication System (README)
------------------------------

Routes:
- /register/  (register new user)
- /login/     (login)
- /logout/    (logout)
- /profile/   (view and edit your profile; requires login)

Files added/modified:
- blog/forms.py: CustomUserCreationForm (adds email)
- blog/views.py: register_view, profile_view
- blog/urls.py: routes for auth views
- blog/templates/blog/*.html: templates for register/login/logout/profile
- settings.py: add LOGIN_REDIRECT_URL, LOGOUT_REDIRECT_URL; ensure 'blog' in INSTALLED_APPS

Usage:
1. python manage.py makemigrations
2. python manage.py migrate
3. python manage.py createsuperuser
4. python manage.py runserver

Security:
- All forms include CSRF tokens.
- Passwords handled by Django's forms (secure hashing).
- Profile page is protected with @login_required.

Testing:
- Manual: Register -> Login -> Edit Profile -> Verify DB changes.
- Automated: run `python manage.py test blog` for the basic test included.

