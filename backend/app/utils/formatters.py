from typing import Union

def format_inr(amount: Union[int, float]) -> str:
    """
    Format a numeric monetary amount into the Indian Rupee numbering format (₹).
    Example: 100000 -> ₹1,00,000
    """
    if amount is None:
        return "₹0"
    
    val_str = f"{abs(amount):.2f}"
    parts = val_str.split(".")
    integer_part = parts[0]
    decimal_part = parts[1]

    if len(integer_part) <= 3:
        formatted = integer_part
    else:
        last3 = integer_part[-3:]
        rest = integer_part[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        formatted = ",".join(groups) + "," + last3

    sign = "-" if amount < 0 else ""
    return f"{sign}₹{formatted}.{decimal_part}" if decimal_part != "00" else f"{sign}₹{formatted}"
