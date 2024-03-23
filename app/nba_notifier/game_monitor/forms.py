# game_monitor/forms.py
from django import forms
from phonenumber_field.formfields import PhoneNumberField

class PhoneForm(forms.Form):
    phone_number = PhoneNumberField()