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


@register.filter(name='client_display_name')
def client_display_name(name, lang='en'):
    """
    Extracts appropriate client name based on language:
    EN: returns secondary English name if found, else original name.
    HI: returns primary Hindi/Devanagari name if found, else original name.
    """
    if not name:
        return ""
    if lang == 'hi':
        return client_primary_name(name)
    sec = client_secondary_name(name)
    return sec if sec else client_primary_name(name)


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
    import re
    num_m = re.search(r'\d+', val_str)
    page_num = num_m.group(0) if num_m else val_str
    if lang == 'hi':
        return f"पृष्ठ {page_num}"
    return f"Page {page_num}"

@register.filter(name='strip_rni_prefix')
def strip_rni_prefix(val):
    """
    Strip repeated 'RNI Reg. No.' or 'पंजीयन क्र.' prefixes to avoid duplicate labels.
    """
    if not val:
        return ""
    import re
    cleaned = re.sub(
        r'^(?:RNI\s*(?:Reg\.?\s*)?(?:No\.?)?[:\s-]*|पंजीयन\s*क्र\.?[:\s-]*)',
        '',
        str(val).strip(),
        flags=re.IGNORECASE
    )
    return cleaned.strip()


@register.filter(name='office_address_display')
def office_address_display(address, lang='en'):
    """
    Return appropriate language variant of the official newspaper address.
    """
    if not address:
        return ""
    addr_str = str(address).strip()
    if lang == 'hi':
        return client_primary_name(addr_str)
    
    # If bilingual in parentheses like: प्रेस परिसर (Press Complex)
    sec = client_secondary_name(addr_str)
    if sec:
        return sec
    
    # Standard default address mapping
    if "प्रेस परिसर" in addr_str and "एम.जी. रोड" in addr_str:
        return "Press Complex, M.G. Road, Indore (M.P.) - 452001"
    
    return addr_str

