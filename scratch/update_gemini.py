with open('GEMINI.md', 'r', encoding='utf-8') as f:
    text = f.read()

target = '    - Automated test suite: 28/28 tests passing (100% OK).'

addition = """
  - **PDF & Browser Print Invoice Comprehensive Overhaul (`billing/templates/billing/bill_pdf.html`)**:
    - **A4 Proportions & Visual Rhythm**:
      - Replaced cramped margins and awkward voids with an authoritative broadsheet newspaper invoice sheet (`width: 190mm; border: 1.5px solid #1c1917; padding: 8mm 10mm;`).
      - Balanced vertical padding across all sections (Masthead, Meta Grid, Particulars Ledger, Totals, Terms, and Payment Desk), ensuring natural cohesive flow on screen and on print/PDF.
    - **Eliminated RNI Prefix Duplication**:
      - Added `strip_rni_prefix` template filter in `billing/templatetags/billing_tags.py`.
      - Strips redundant `"RNI Reg. No."` prefixes, cleanly rendering `RNI Reg. No.: MP-HIN/2018/12345` (English) and `आर.एन.आई. पंजीयन: MP-HIN/2018/12345` (Hindi) with zero duplication.
    - **Zero-Dependency Pure-Python English Number Converter**:
      - Added `_number_to_english_words(num)` in `billing/utils.py` supporting Indian numbering (Crores, Lakhs, Thousands, Hundreds).
      - Guaranteed fallback in `amount_in_words_bilingual`: Never outputs raw numeric strings like `"Rupees 3500 Only"`; always spells out amounts completely (e.g. `"Rupees Three Thousand Five Hundred Only"`).
    - **Intelligent Ledger Table Sizing & Previous Due Handling**:
      - Handled `base_amount == 0.00` settlement bills cleanly by rendering the primary line item as `"Previous Outstanding Balance / Account Settlement"` with clear notes, preventing confusing 0.00 publication line items.
      - Increased line item padding (`10px 10px`) with high contrast ink typography.
    - **Official Cashier Receipt & Dynamic QR Desk**:
      - **Settled / Paid Bills**: Render an official green cashier seal medallion (`✓ PAYMENT SETTLED • Zero Balance Outstanding (Official Cashier Clearance)`), eliminating empty void cells.
      - **Unpaid / Partial Bills**: Render high-contrast 86x86px dynamic NPCI UPI QR code with amount callout and multi-app support (GPay, PhonePe, Paytm, BHIM).
      - **Dual Authentication Modes**: Computer Generated (`sign=0`, Information Technology Act 2000 digital verification badge) vs Physical Seal & Sign (`sign=1`, 48px clearance for physical stamp and signature).
    - **Language & Office Address Polish**:
      - Added `office_address_display` filter for pristine English and Hindi office addresses.
      - Sticky top print toolbar equipped with Bootstrap Icons (`bi-printer`, `bi-display`, `bi-pen`, `bi-arrow-left`) and clean `@media print` rules hiding non-printable controls.
    - **Verification**: Captured and validated 4 distinct CDP screenshots (`pdf_bill3_en_comp.png`, `pdf_bill3_hi_comp.png`, `pdf_bill3_en_sign.png`, `pdf_bill2_en_unpaid.png`).
    - **Automated Unit Tests**: Added `test_pdf_rni_no_duplication_and_settlement`; 29/29 automated unit tests passing (100% OK)."""

if target in text:
    new_text = text.replace(target, target + addition, 1)
    with open('GEMINI.md', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("SUCCESS: GEMINI.md updated!")
else:
    print("ERROR: target not found in GEMINI.md")
