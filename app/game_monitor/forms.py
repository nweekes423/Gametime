from django import forms
from django.core.validators import RegexValidator


class PhoneForm(forms.Form):
    phone_number = forms.CharField(
        max_length=17,
        label="Phone Number",
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Enter a valid phone number, such as '+14155552671'.",
            )
        ],
    )

    team = forms.CharField(
        max_length=10,
        required=False,
    )
