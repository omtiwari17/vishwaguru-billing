import decimal
from decimal import Decimal
from django import template

register = template.Library()


@register.filter(name='indian_currency')
def indian_currency(value):
    """
    Format a number in Indian currency style: ₹1,84,200.
    Omits paise (.00) unless paise exist (e.g. ₹1,84,200.50).
    """
    if value is None or value == "":
        return "₹0"

    try:
        if isinstance(value, Decimal):
            d = value
        else:
            d = Decimal(str(value))
    except (decimal.InvalidOperation, TypeError, ValueError):
        return f"₹{value}"

    is_negative = d < 0
    abs_d = abs(d)

    int_part = int(abs_d)
    cents_part = round((abs_d % 1) * 100)

    # Format integer part with Indian grouping: last 3 digits, then groups of 2
    s = str(int_part)
    if len(s) > 3:
        last3 = s[-3:]
        rest = s[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        formatted_int = ",".join(groups) + "," + last3
    else:
        formatted_int = s

    if cents_part > 0:
        formatted = f"{formatted_int}.{cents_part:02d}"
    else:
        formatted = formatted_int

    prefix = "-₹" if is_negative else "₹"
    return f"{prefix}{formatted}"


@register.filter(name='bill_count_label')
def bill_count_label(count, lang='en'):
    """
    Return formatted count with noun:
    EN: 1 bill, 2 bills, 0 bills
    HI: 1 बिल, 2 बिल, 0 बिल
    """
    try:
        cnt = int(count)
    except (ValueError, TypeError):
        cnt = 0

    if lang == 'hi':
        return f"{cnt} बिल"
    return f"{cnt} bill" if cnt == 1 else f"{cnt} bills"


@register.filter(name='bill_noun')
def bill_noun(count, lang='en'):
    """
    Return just the noun:
    EN: bill or bills
    HI: बिल
    """
    try:
        cnt = int(count)
    except (ValueError, TypeError):
        cnt = 0

    if lang == 'hi':
        return "बिल"
    return "bill" if cnt == 1 else "bills"


@register.filter(name='client_primary_name')
def client_primary_name(name):
    """
    Extracts the primary name from a bilingual string like:
    'पटेल ऑटोमोबाइल्स (Patel Automobiles)' -> 'पटेल ऑटोमोबाइल्स'
    If no parentheses, returns the full string.
    """
    if not name:
        return ""
    import re
    m = re.match(r'^(.*?)\s*\(.*?\)$', str(name).strip())
    if m:
        return m.group(1).strip()
    return str(name).strip()


@register.filter(name='client_secondary_name')
def client_secondary_name(name):
    """
    Extracts the secondary English name from a bilingual string like:
    'पटेल ऑटोमोबाइल्स (Patel Automobiles)' -> 'Patel Automobiles'
    If no parentheses, returns empty string.
    """
    if not name:
        return ""
    import re
    m = re.match(r'^.*?\s*\((.*?)\)$', str(name).strip())
    if m:
        return m.group(1).strip()
    return ""


@register.filter(name='format_page')
def format_page(value, lang='en'):
    """
    Format page number string according to language:
    EN: "Page 1", "Page 4"
    HI: "पृष्ठ 1", "पृष्ठ 4"
    """
    if not value:
        return ""
    val_str = str(value).strip()
    if lang == 'hi':
        import re
        val_hi = re.sub(r'^(page|pg\.?)\s*', 'पृष्ठ ', val_str, flags=re.IGNORECASE)
        if val_hi.isdigit():
            val_hi = f"पृष्ठ {val_hi}"
        return val_hi
    return val_str


