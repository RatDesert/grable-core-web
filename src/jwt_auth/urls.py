from django.urls import path

from .views import refresh_tokens, logout, LoginView, sessions


urlpatterns = [
    # path('login/', login, name="auth_token_obtain"),
    path("refresh_tokens/", refresh_tokens, name="auth_token_refresh"),
    path("logout/", logout, name="auth_token_revoke"),
    path("sessions/", sessions, name="auth_sessions_details"),
    path("login/", LoginView.as_view(), name="login"),
]

# prefix for cookie namespace
