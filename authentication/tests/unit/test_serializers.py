from django.test import TestCase

from authentication.serializers import SignUpSerializer, LoginSerializer
from authentication.models import User


class SignUpSerializerTestCase(TestCase):
    """Unit tests for SignUpSerializer"""

    def test_valid_data_creates_serializer(self):
        """Test serializer accepts valid data"""
        data = {
            "email": "test@example.com",
            "password": "validpassword123"
        }
        serializer = SignUpSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_email_lowercase_and_stripped(self):
        """Test email is lowercased and stripped"""
        data = {
            "email": "  TEST@EXAMPLE.COM  ",
            "password": "validpassword123"
        }
        serializer = SignUpSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["email"], "test@example.com")

    def test_duplicate_email_validation(self):
        """Test duplicate email raises validation error"""
        User.objects.create(email="test@example.com")

        data = {
            "email": "test@example.com",
            "password": "validpassword123"
        }
        serializer = SignUpSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_duplicate_email_case_insensitive(self):
        """Test duplicate email check is case-insensitive"""
        User.objects.create(email="test@example.com")

        data = {
            "email": "TEST@EXAMPLE.COM",
            "password": "validpassword123"
        }
        serializer = SignUpSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_password_min_length(self):
        """Test password enforces minimum length"""
        data = {
            "email": "test@example.com",
            "password": "short"
        }
        serializer = SignUpSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_missing_email(self):
        """Test missing email raises error"""
        data = {"password": "validpassword123"}
        serializer = SignUpSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_missing_password(self):
        """Test missing password raises error"""
        data = {"email": "test@example.com"}
        serializer = SignUpSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_create_hashes_password(self):
        """Test create method hashes password"""
        data = {
            "email": "test@example.com",
            "password": "validpassword123"
        }
        serializer = SignUpSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        # Password should be hashed
        self.assertNotEqual(user.password, "validpassword123")
        self.assertTrue(user.check_password("validpassword123"))

    def test_read_only_fields_ignored(self):
        """Test read_only_fields are ignored"""
        data = {
            "email": "test@example.com",
            "password": "validpassword123",
            "display_name": "Should Be Ignored",  # read_only
        }
        serializer = SignUpSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        # display_name should not be set from input
        self.assertNotEqual(user.display_name, "Should Be Ignored")


class LoginSerializerTestCase(TestCase):
    """Unit tests for LoginSerializer"""

    def setUp(self):
        self.user = User.objects.create(email="test@example.com")
        self.user.set_password("validpassword123")
        self.user.save()

    def test_valid_credentials(self):
        """Test serializer accepts valid credentials"""
        data = {
            "email": "test@example.com",
            "password": "validpassword123"
        }
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], self.user)

    def test_email_case_insensitive(self):
        """Test email authentication is case-insensitive"""
        data = {
            "email": "TEST@EXAMPLE.COM",
            "password": "validpassword123"
        }
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], self.user)

    def test_email_stripped(self):
        """Test email is stripped of whitespace"""
        data = {
            "email": "  test@example.com  ",
            "password": "validpassword123"
        }
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], self.user)

    def test_wrong_password(self):
        """Test wrong password raises validation error"""
        data = {
            "email": "test@example.com",
            "password": "wrongpassword123"
        }
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("error", serializer.errors)

    def test_non_existent_email(self):
        """Test non-existent email raises validation error"""
        data = {
            "email": "nonexistent@example.com",
            "password": "validpassword123"
        }
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("error", serializer.errors)

    def test_missing_email(self):
        """Test missing email raises error"""
        data = {"password": "validpassword123"}
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_missing_password(self):
        """Test missing password raises error"""
        data = {"email": "test@example.com"}
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_invalid_email_format(self):
        """Test invalid email format raises error"""
        data = {
            "email": "not-an-email",
            "password": "validpassword123"
        }
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)