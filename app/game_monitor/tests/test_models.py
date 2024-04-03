from django.core.exceptions import ValidationError
from django.test import TestCase

from game_monitor.models import UserPhone


class UserPhoneModelTests(TestCase):
    def test_valid_phone_number(self):
        # Test that a valid phone number is saved successfully
        user_phone = UserPhone(phone_number="+1234567890")
        user_phone.save()
        self.assertEqual(UserPhone.objects.count(), 1)

    def test_invalid_phone_number(self):
        # Test that saving an invalid phone number raises a ValidationError
        with self.assertRaises(ValidationError):
            user_phone = UserPhone(phone_number="invalid_number")
            user_phone.full_clean()
