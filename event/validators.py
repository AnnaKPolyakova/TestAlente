from datetime import datetime

from rest_framework.exceptions import ValidationError


def data_time_validator(value):
    if value.timestamp() < datetime.now().timestamp():
        raise ValidationError(
            f"{value} - значение даты и времени должно быть больше текущего"
        )
