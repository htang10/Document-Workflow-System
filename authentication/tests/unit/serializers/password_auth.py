from django.test import TestCase

from authentication.serializers import SignUpSerializer, LoginSerializer
from authentication.models import User

from authentication.tests.unit.serializers.email import EmailFieldTestMixin


class SignUpSerializerTestCase(EmailFieldTestMixin, TestCase):
    """Unit tests for sign-up serializer"""

    def setUp(self):
        self.email = "test@example.com"
        self.password = "validpassword123"
        self.serializer_class = SignUpSerializer

    def get_payload(self, **overrides):
        base = {"email": self.email, "password": self.password}
        return {**base, **overrides}

    def test_duplicate_email_validation(self):
        """Test duplicate email raises validation error"""
        User.objects.create(email=self.email)
        serializer = self.serializer_class(data=self.get_payload())

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_password_min_length(self):
        """Test password enforces minimum length"""
        serializer = self.serializer_class(data=self.get_payload(password="short"))

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_valid_data(self):
        """Test serializer accepts valid data"""
        serializer = self.serializer_class(data=self.get_payload(display_name="Read-only"))

        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        # display_name should not be set from input
        self.assertNotEqual(user.display_name, "Read-only")
        # Password should be hashed
        self.assertNotEqual(user.password, self.password)
        self.assertTrue(user.check_password(self.password))


class LoginSerializerTestCase(EmailFieldTestMixin, TestCase):
    """Unit tests for login serializer"""

    def setUp(self):
        self.user = User.objects.create(email="test@example.com")
        self.user.set_password("validpassword123")
        self.user.save()
        self.serializer_class = LoginSerializer

    def get_payload(self, **overrides):
        base = {"email": self.user.email, "password": self.user.password}
        return {**base, **overrides}

    def test_invalid_credentials(self):
        """Test login with non-existent email or incorrect password raises validation error"""
        serializer = self.serializer_class(data=self.get_payload(email="nonexist@example.com", password="wrongpassword"))

        self.assertFalse(serializer.is_valid())
        self.assertIn("error", serializer.errors)

    def test_valid_credentials(self):
        """Test login with valid credentials"""
        serializer = self.serializer_class(data=self.get_payload())

        self.assertTrue(serializer.is_valid())
        self.assertIn("refresh", serializer.context)
        self.assertIn("access", serializer.context)


