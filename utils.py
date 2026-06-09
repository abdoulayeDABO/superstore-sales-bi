# 1,000 -> 1K

def format_number(n: int) -> str:
    """
    Formate un entier en notation courte.
    >>> format_number(1_500)
    '1.5K'
    >>> format_number(1_000_000)
    '1M'
    """
    thresholds = [
        (1_000_000_000, 'B'),
        (1_000_000,     'M'),
        (1_000,         'K'),
    ]
    for divisor, suffix in thresholds:
        if n >= divisor:
            value = n / divisor
            # 1500 -> "1.5K" au lieu de "1K"
            return f"{value:.0f}{suffix}" if value == int(value) else f"{value:.1f}{suffix}"
    return str(n)


if __name__ == "__main__":
    print(format_number(1500))
    print(format_number(15000))
    print(format_number(1000000))