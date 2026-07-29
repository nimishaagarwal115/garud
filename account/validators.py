from django.core.exceptions import ValidationError
import re

class FourDigitNumericPasswordValidator:
    def validate(self, password, user=None):
        if not re.fullmatch(r"\d{4}", password):
            raise ValidationError(
                "Password must be exactly 4 digits.",
                code='password_not_4_digits',
            )

    def get_help_text(self):
        return "Your password must be exactly 4 digits."