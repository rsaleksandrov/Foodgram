import re

from django.core.exceptions import ValidationError


def color_code_validate(value):
    hex_parent = re.compile('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
    if not hex_parent.match(value):
        raise ValidationError(
            'Код цвета задаётся в формате #dddddd, '
            'где d принимает значения из диапозона [0-9, A-F]'
        )
