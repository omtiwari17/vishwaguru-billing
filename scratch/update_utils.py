import sys

with open('billing/utils.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Normalize line endings for replacement
text = text.replace('\r\n', '\n')

old_block = """def amount_in_words_bilingual(amount):
    \"\"\"
    Generate bilingual amount in words:
    Hindi: पाँच हज़ार रुपये मात्र
    English: Five Thousand Rupees Only
    \"\"\"
    amt_dec = Decimal(str(amount or '0.00'))
    total_int = int(amt_dec)
    paise = int(round((amt_dec - total_int) * 100))

    # Hindi words
    hindi_part = _number_to_hindi_words(total_int)
    if paise > 0:
        hindi_words = f"{hindi_part} रुपये {HINDI_ONES.get(paise, str(paise))} पैसे मात्र"
    else:
        hindi_words = f"{hindi_part} रुपये मात्र"

    # English words
    try:
        from num2words import num2words
        eng_raw = num2words(total_int, lang='en_IN').replace(',', '').title()
        if paise > 0:
            eng_paise = num2words(paise, lang='en_IN').title()
            eng_words = f"Rupees {eng_raw} and {eng_paise} Paise Only"
        else:
            eng_words = f"Rupees {eng_raw} Only"
    except Exception:
        eng_words = f"Rupees {total_int} Only"

    return {
        'hindi': hindi_words,
        'english': eng_words,
        'combined': f"{hindi_words} ({eng_words})"
    }"""

new_block = """ENGLISH_ONES = {
    0: "", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
    6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten",
    11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen",
    16: "Sixteen", 17: "Seventeen", 18: "Eighteen", 19: "Nineteen",
    20: "Twenty", 30: "Thirty", 40: "Forty", 50: "Fifty",
    60: "Sixty", 70: "Seventy", 80: "Eighty", 90: "Ninety"
}


def _number_to_english_words(num):
    \"\"\"
    Convert integer up to 99,99,99,999 into English words using the Indian numbering system:
    Crore (1,00,00,000), Lakh (1,00,000), Thousand (1,000), Hundred (100).
    Zero-dependency pure Python fallback that never fails.
    \"\"\"
    if num == 0:
        return "Zero"
    if num < 0:
        return f"Minus {_number_to_english_words(abs(num))}"

    parts = []
    crore = num // 10000000
    num %= 10000000
    if crore > 0:
        parts.append(f"{_number_to_english_words(crore)} Crore")

    lakh = num // 100000
    num %= 100000
    if lakh > 0:
        parts.append(f"{_number_to_english_words(lakh)} Lakh")

    thousand = num // 1000
    num %= 1000
    if thousand > 0:
        parts.append(f"{_number_to_english_words(thousand)} Thousand")

    hundred = num // 100
    num %= 100
    if hundred > 0:
        parts.append(f"{_number_to_english_words(hundred)} Hundred")

    if num > 0:
        if num < 20:
            parts.append(ENGLISH_ONES.get(num, str(num)))
        else:
            tens = (num // 10) * 10
            unit = num % 10
            if unit > 0:
                parts.append(f"{ENGLISH_ONES.get(tens, '')} {ENGLISH_ONES.get(unit, '')}")
            else:
                parts.append(ENGLISH_ONES.get(tens, ''))

    return " ".join(parts).strip()


def amount_in_words_bilingual(amount):
    \"\"\"
    Generate bilingual amount in words:
    Hindi: तीन हज़ार पाँच सौ रुपये मात्र
    English: Rupees Three Thousand Five Hundred Only
    Guaranteed to never return raw numeric strings like 'Rupees 3500 Only'.
    \"\"\"
    amt_dec = Decimal(str(amount or '0.00'))
    total_int = int(amt_dec)
    paise = int(round((amt_dec - total_int) * 100))

    # Hindi words
    hindi_part = _number_to_hindi_words(total_int)
    if paise > 0:
        hindi_words = f"{hindi_part} रुपये {HINDI_ONES.get(paise, str(paise))} पैसे मात्र"
    else:
        hindi_words = f"{hindi_part} रुपये मात्र"

    # English words (Robust pure-Python first, with graceful formatting)
    try:
        from num2words import num2words
        eng_raw = num2words(total_int, lang='en_IN').replace(',', '').title()
        if paise > 0:
            eng_paise = num2words(paise, lang='en_IN').title()
            eng_words = f"Rupees {eng_raw} and {eng_paise} Paise Only"
        else:
            eng_words = f"Rupees {eng_raw} Only"
    except Exception:
        eng_raw = _number_to_english_words(total_int)
        if paise > 0:
            eng_paise = _number_to_english_words(paise)
            eng_words = f"Rupees {eng_raw} and {eng_paise} Paise Only"
        else:
            eng_words = f"Rupees {eng_raw} Only"

    return {
        'hindi': hindi_words,
        'english': eng_words,
        'combined': f"{hindi_words} ({eng_words})"
    }"""

if old_block not in text:
    print("ERROR: old_block not found in utils.py")
    sys.exit(1)

updated = text.replace(old_block, new_block, 1)

with open('billing/utils.py', 'w', encoding='utf-8') as f:
    f.write(updated)

print("SUCCESS: billing/utils.py updated successfully!")
