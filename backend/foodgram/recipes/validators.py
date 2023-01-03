from django.core.exceptions import ValidationError
from re import findall, match


ANTI_PATTERN = r'[^\w\s]'
PATTERN_HEX = r'^#[0-9a-zA-Z]{6}$'


def validate_name(data):
    result = set(findall(ANTI_PATTERN, data))
    if result:
        raise ValidationError(
            f'В названии недопустимые символы: {"".join(result)}'
        )
    return data


def validate_hex(data):
    result = match(PATTERN_HEX, data).string
    if result is None:
        raise ValidationError(
            'Не соответствует коду hex цвета'
        )
    return data
