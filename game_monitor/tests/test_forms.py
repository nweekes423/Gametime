from django.test import TestCase

from game_monitor.forms import PhoneForm


class PhoneFormTests(TestCase):
    def test_valid_phone_form(self):
        form = PhoneForm(data={"phone_number": "+1234567890"})
        self.assertTrue(form.is_valid())

    def test_invalid_phone_form(self):
        form = PhoneForm(data={"phone_number": "invalid_number"})
        self.assertFalse(form.is_valid())
