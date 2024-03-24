# game_monitor/tests/test_forms.py
from django.test import TestCase
from game_monitor.forms import PhoneForm

class PhoneFormTests(TestCase):
    def test_valid_phone_form(self):
    	# Test that a valid phone number in the form data is considered valid
        form = PhoneForm(data={"phone_number": "+15105286441"})
        self.assertTrue(form.is_valid())

    def test_invalid_phone_form(self):
    	# Test that an invalid phone number in the form data is considered invalid
        form = PhoneForm(data={"phone_number": "invalid_number"})
        self.assertFalse(form.is_valid())
        print(form.errors)  # Add this line for debug information
