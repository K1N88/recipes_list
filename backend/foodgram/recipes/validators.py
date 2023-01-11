from django.core.validators import RegexValidator


ANTI_PATTERN = r'[^\w\s]'
PATTERN_HEX = r'^#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$'


def validate_name(data):
    RegexValidator(regex=ANTI_PATTERN, inverse_match=True)(data)


def validate_hex(data):
    RegexValidator(regex=PATTERN_HEX)(data)
