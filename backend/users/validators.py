from rest_framework import serializers

from users.constants import API_USER_INFO_NAME


def validate_username_include_me(value):
    if value == API_USER_INFO_NAME:
        raise serializers.ValidationError(
            f"Использовать имя {API_USER_INFO_NAME} в качестве username "
            f"запрещено")
    return value
