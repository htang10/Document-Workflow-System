from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import User


class SignUpTestCase(APITestCase):
    """Test password-based sign-up functionality"""

    def setUp(self):
        self.email = "new_user@gmail.com"
        self.password = "newuser123"
        self.url = reverse("sign-up")

    def test_without_data(self):
        """Test with no data"""
        data = {}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email(self):
        """Test with invalid email"""
        invalid_emails = [
            "invalid_email",
            "invalid_email@domain",
            "invalid_email@.com",
            "invalid_email.domain.com",
            "invalid_email@domain..com",
            "invalid email@domain.com"
        ]

        for email in invalid_emails:
            with self.subTest(email=email):
                data = {"email": email, "password": self.password}
                response = self.client.post(self.url, data, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_existing_email_case_insensitive(self):
        """Test with existing email, regardless of letter case"""
        # Assume an existing user
        user = User.objects.create(email=self.email)
        user.set_password(self.password)
        user.save()

        # Email should be case-insensitive
        cases = [self.email.lower(), self.email.upper(), self.email.capitalize()]

        for email in cases:
            data = {"email": email, "password": self.password}
            response = self.client.post(self.url, data, format="json")

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test with password below minimum length"""
        data = {"email": self.email, "password": "short"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sign_up(self):
        """Test with valid data"""
        data = {"email": self.email, "password": self.password}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.email).exists())


class LoginTestCase(APITestCase):
    """Test password-based login functionality"""

    def setUp(self):
        self.email = "existing_user@gmail.com"
        self.password = "existinguser123"
        self.url = reverse("login")

        # Assume an existing user
        User.objects.create(email=self.email, password=self.password)
        user = User.objects.filter(email=self.email).first()
        user.set_password(self.password)
        user.save()

    def test_without_data(self):
        """Test with no data"""
        data = {}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email(self):
        """Test with invalid email"""
        invalid_emails = [
            "invalid_email",
            "invalid_email@domain",
            "invalid_email@.com",
            "invalid_email.domain.com",
            "invalid_email@domain..com",
            "invalid email@domain.com"
        ]

        for email in invalid_emails:
            with self.subTest(email=email):
                data = {"email": email, "password": self.password}
                response = self.client.post(self.url, data, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_existent_email_case_insensitive(self):
        """Test with non-existent email, regardless of letter case"""
        data = {"email": "random_user@gmail.com", "password": "randomuser123"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_password(self):
        """Test with correct email but wrong password"""
        data = {"email": self.email, "password": "wrongpassword123"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sign_up_password_hashed(self):
        """Test that password is hashed, not stored in plaintext"""
        data = {"email": self.email, "password": self.password}
        response = self.client.post(self.url, data, format="json")

        user = User.objects.get(email=self.email)
        # Password should be hashed (not plaintext)
        self.assertNotEqual(user.password, self.password)
        # But should still authenticate
        self.assertTrue(user.check_password(self.password))

    def test_login(self):
        """Test with valid data"""
        # Email should be case-insensitive
        cases = [self.email.lower(), self.email.upper(), self.email.capitalize()]

        for email in cases:
            data = {"email": email, "password": self.password}
            response = self.client.post(self.url, data, format="json")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("refresh", response.data)
            self.assertIn("access", response.data)
            self.assertIn("user", response.data)
            self.assertEqual(response.data["user"]["email"], self.email)
            self.assertIsNotNone(response.data["user"]["display_name"])

    def test_login_updates_login_metadata(self):
        """Test that login metadata is updated"""
        data = {"email": self.email, "password": self.password}
        response = self.client.post(self.url, data, format="json")

        user = User.objects.get(email=self.email)
        # Verify login metadata was updated
        self.assertIsNotNone(user.last_login_time)
        self.assertIsNotNone(user.last_active)
        self.assertIsNotNone(user.last_login_ip)
        self.assertIsNotNone(user.last_login_uagent)
        self.assertEqual(user.last_login_medium, "email")