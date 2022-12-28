from django.core.exceptions import ValidationError
from re import findall


ANTI_PATTERN = r'[^\w.@+-]'  # ^[\w.@+-]+\z


def validate_username(data):
    if data == 'me':
        raise ValidationError('Имя "me" не использовать!')

    result = set(findall(ANTI_PATTERN, data))
    if result:
        raise ValidationError(
            f'В имени недопустимые символы: {"".join(result)}'
        )
    return data
