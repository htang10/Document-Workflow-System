from django.utils import timezone


def get_client_ip(request):
    """Retrieves the client ip address of the current request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def update_user_login_metadata(user, request):
    """
    Updates the user login metadata including timestamp, ip address, user agent and medium.
    """
    now = timezone.now()
    user.last_login_time = now
    user.last_active = now
    user.last_login_ip = get_client_ip(request)
    user.last_login_uagent = request.META.get("HTTP_USER_AGENT", "")
    user.last_login_medium = "email"
    user.save(update_fields=[
        "last_login_time", "last_active", "last_login_ip",
        "last_login_uagent", "last_login_medium"
    ])
    return user