import random
import string
import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(default=uuid.uuid7, editable=False, primary_key=True)

    # identity
    email = models.EmailField(max_length=255, unique=True) # Required

    # UI
    display_name = models.CharField(max_length=255, default="")

    # authorization
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)

    # tracking metrics
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Joined")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Modified At")
    last_active = models.DateTimeField(null=True)
    last_login_time = models.DateTimeField(null=True)
    last_login_ip = models.CharField(max_length=255, blank=True)
    last_login_medium = models.CharField(max_length=20, default="email")
    last_login_uagent = models.TextField(blank=True)
    last_logout_time = models.DateTimeField(null=True)
    last_logout_ip = models.CharField(max_length=255, blank=True)

    # masking
    masked_at = models.DateTimeField(null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        db_table = "users"
        ordering = ["-created_at"]

    def save(self, **kwargs):
        self.email = self.email.lower().strip()

        if not self.display_name:
            self.display_name = (
                self.email.split("@")[0]
                if len(self.email.split("@"))
                else "".join(random.choice(string.ascii_letters) for _ in range(6))
            )

        if self.is_superuser:
            self.is_staff = True

        super().save(**kwargs)
