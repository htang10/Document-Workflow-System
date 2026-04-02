class EmailFieldTestMixin:
    """Shared email validation tests for any serializer that has an email field."""

    def get_payload(self, **overrides):
        """Each subclass defines its own valid base payload."""
        raise NotImplementedError

    def test_invalid_email_format(self):
        payload = self.get_payload(email="not-an-email")
        serializer = self.serializer_class(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_email_is_lowercased_and_stripped(self):
        email = self.get_payload().get("email")
        payload = self.get_payload(email="  TeSt@Example.COM  ")
        serializer = self.serializer_class(data=payload)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["email"], email)
