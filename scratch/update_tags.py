with open('billing/templatetags/billing_tags.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\r\n', '\n')

new_filters = """

@register.filter(name='strip_rni_prefix')
def strip_rni_prefix(val):
    \"\"\"
    Strip repeated 'RNI Reg. No.' or 'पंजीयन क्र.' prefixes to avoid duplicate labels.
    \"\"\"
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
    \"\"\"
    Return appropriate language variant of the official newspaper address.
    \"\"\"
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
"""

if "strip_rni_prefix" not in text:
    text = text.rstrip() + new_filters + "\n"
    with open('billing/templatetags/billing_tags.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESS: Added strip_rni_prefix and office_address_display to billing_tags.py")
else:
    print("ALREADY EXISTS: strip_rni_prefix in billing_tags.py")
