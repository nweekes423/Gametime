from django import forms


class PhoneForm(forms.Form):
    phone_number = forms.CharField(label="Phone Number", max_length=15)
