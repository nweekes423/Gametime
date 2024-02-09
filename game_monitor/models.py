from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

# Create your models here.


class UserPhone(models.Model):
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, blank=True
    )  # adjust the max_length as needed

    def save(self, *args, **kwargs):
        try:
            # Validate the phone number
            self.full_clean()
        except ValidationError as e:
            # Here, you can customize the error message or use e.message_dict
            custom_error_message = "Invalid phone number. Please enter a number in the format: '+999999999'. Up to 15 digits allowed."
            raise ValidationError(custom_error_message)

        super(UserPhone, self).save(*args, **kwargs)
