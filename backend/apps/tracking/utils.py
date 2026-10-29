from decimal import ROUND_HALF_UP, Decimal


def round1(value):
    return Decimal(value).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
