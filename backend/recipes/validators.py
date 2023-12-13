import base64
import binascii

from django.core.validators import RegexValidator
from rest_framework.exceptions import ValidationError

validate_color = RegexValidator(
    regex=r'^#(?:[0-9a-fA-F]{3}){1,2}$',
    message='Значение должно начинаться с # и содержать 3 или 6 HEX символов')


def validate_base64_image(value):
    try:
        # Декодируем Base64-строку в бинарные данные
        decoded_data = base64.b64decode(value)

        # Проверяем, являются ли декодированные данные изображением
        # В данном примере, мы проверяем,
        # что первые несколько байт начинаются с маркера JPEG или PNG
        if not (decoded_data.startswith(
                b'\xff\xd8') or decoded_data.startswith(b'\x89PNG')):
            raise ValidationError("Invalid Base64 image data")
    except (TypeError, binascii.Error):
        raise ValidationError("Invalid Base64 string")
