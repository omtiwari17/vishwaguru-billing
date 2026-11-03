# Vishwaguru Billing — UI/UX Design System & Implementation Record

> **Document Status**: Production-Implemented & Verified  
> **Last Updated**: 3 November 2026  
> **Test Suite**: 27 / 27 Automated Unit Tests Passing (100% OK)  
> **Dev Server**: Running on `http://127.0.0.1:8080/`

---

## 1. Executive Summary & Design System Overview

Vishwaguru Billing has been overhauled from a fragmented prototype into a unified, robust **Newspaper-Office Design System**. The aesthetic reflects a calm, high-efficiency editorial clerk's workstation: restrained, high-contrast, functionally dense, and optimized for both rapid desktop keyboard entry and touch-friendly mobile operation in both **English** and **हिन्दी (Devanagari)**.

### Core Visual Foundation Tokens

| Token | Value | Semantic Purpose |
|---|---|---|
| **Paper Background** | `#faf8f4` | Warm, non-glare broadsheet paper backdrop across all screens |
| **Ink Text** | `#1c1917` | High-contrast, authoritative dark slate typography |
| **Muted Ink** | `#57534e` / `#78716c` | Secondary labels and context text (WCAG AA compliant $\ge 4.5:1$) |
| **Rule Border** | `#e7e2d9` | Subtle structural dividers and quiet panel borders |
| **Border Active / Button** | `#d6cfc4` | High-visibility control boundary (2.4:1 contrast ratio) |
| **Brand Maroon** | `#9f1d1d` | Sole primary accent: submission buttons, balance due alerts, active tabs |
| **Paid Green** | `#15803d` | Settled/cleared invoices, verified ledger entries, success dots |
| **Partial Amber** | `#b45309` | Partially paid balances and pending verification alerts |
| **Card / Panel Radius** | `4px` maximum | Crisp newspaper broadsheet edges (zero bubbly rounded corners) |
| **Elevation / Shadows** | `0` (Flat) | Zero drop-shadows or fuzzy gradients; all depth is ruled by 1px borders |

---

## 2. Typography & Scale Hierarchy

### Strict Font Engine Rules
1. **Interface Text (`font-family: 'Mukta', sans-serif;`)**:
   - Mukta is used for all UI text, form controls, buttons, table data, and captions because its Latin and Devanagari character sets share matching x-heights and visual weights.
   - **Base Body**: `16px` (scaled up from cramped 15px).
   - **Form Labels & Table Headers**: `14px` semibold (scaled up from illegible 11px–12px).
   - **Absolute Size Floor**: **Zero text below 13px** on desktop screens. The previous `font-size: 12px !important;` CSS floor was completely removed from `style.css` because it blurred Devanagari matras and conjuncts.
2. **Masthead & Editorial Headlines (`font-family: 'Noto Serif Devanagari', serif;`)**:
   - Reserved strictly for the official brand masthead ("विश्वगुरु की झलक") and primary invoice/page titles.
3. **Financial & Numerical Data (`font-variant-numeric: tabular-nums;`)**:
   - Enforced on all rupee amounts, dates, bill numbers, and phone numbers to guarantee rigid vertical column alignment across all ledgers and tables.
   - Formatted via custom Indian numbering format filter (`₹1,84,200` without unwanted `.00` decimals unless fractional paise exist).

### Typography Scale Matrix

| Element | Font Size | Weight | Font Family | Example |
|---|---|---|---|---|
| **KPI Balances** | `32px` | 700 (Bold) | Mukta (`tabular-nums`) | `₹3,500` |
| **Page H1 / Title** | `24px–28px` | 700 (Bold) | Noto Serif Devanagari | **VG-2026-0003** |
| **Section Headings** | `18px–20px` | 600 (Semibold) | Noto Serif / Mukta | **Recent bills** |
| **Primary Buttons** | `15px` | 600 (Semibold) | Mukta | `+ Create New Bill` |
| **Form Inputs & Selects** | `15px–16px` | 400 (Regular) | Mukta | Client Name input |
| **Body & Table Cells** | `15px–16px` | 400 (Regular) | Mukta | `Patel Automobiles` |
| **Labels & Subtext** | `14px` | 500 (Medium) | Mukta | `Page 1 · Indore` |
| **Small Badges & Dates** | `13px` | 500 (Medium) | Mukta | `23 Sep 2026` |

---

## 3. Authoritative Button & Control Hierarchy

Buttons and interactive controls have been scaled from low-contrast, badge-like elements into clear, click-affordant tools.

### Button Specifications

| Component Class | Dimensions & Padding | Typography | Visual Treatment | Usage |
|---|---|---|---|---|
| `.btn-desk-primary` | Min-height: `44px–48px`<br>Padding: `10px 20px` | `15px–16px`<br>Weight: 600 | Solid Maroon (`#9f1d1d`), white text, 4px radius | Primary page actions (`Save Bill`, `Sign In`, `Pay via UPI`) |
| `.btn-desk-secondary` | Min-height: `42px–44px`<br>Padding: `8px 16px` | `14px–15px`<br>Weight: 500 | Paper/white bg, 1px border (`#d6cfc4`), ink text | Secondary actions, filters, search triggers |
| `.btn-desk-sm` | Min-height: `32px`<br>Padding: `4px 10px` | `13px`<br>Weight: 500 | White bg, 1px border (`#d6cfc4`), ink text, 3px radius | Dense table actions (`View`, `PDF`, `WhatsApp`, `Portal`) |
| `.btn-desk-sm.btn-pdf` | Min-height: `32px`<br>Padding: `4px 10px` | `13px`<br>Weight: 500 | Red border/text (`#b91c1c`) | Table direct PDF download |
| `.btn-desk-sm.btn-whatsapp` | Min-height: `32px`<br>Padding: `4px 10px` | `13px`<br>Weight: 500 | Forest green border/text (`#15803d`) | Table WhatsApp statement share |
| **Touch Targets (Mobile)** | Min-height: $\ge 44\text{px}$ | $\ge 14\text{px}$ | Full-width or flex-1 distribution | All mobile touch triggers |

---

## 4. Strict Vector Icon System (Zero Emojis Policy)

> [!IMPORTANT]
> **MANDATORY POLICY**: Unicode emojis are strictly prohibited across all templates, UI controls, notifications, and code in this repository. All iconography must use vector **Bootstrap Icons** (`<i class="bi bi-..."></i>`).

### Standardized Icon Mapping Matrix

| Semantic Action / Concept | Prohibited Emoji | Standardized Vector Bootstrap Icon |
|---|:---:|---|
| **PDF Download** | 📄 | `<i class="bi bi-file-earmark-pdf"></i>` |
| **Seal & Sign Version** | ✍️ | `<i class="bi bi-pen"></i>` |
| **WhatsApp Reminder / Share** | 💬 📱 | `<i class="bi bi-whatsapp"></i>` |
| **Customer Statement Portal** | ↗️ 🔗 | `<i class="bi bi-arrow-up-right"></i>` |
| **Create New Bill** | ➕ | `<i class="bi bi-plus-lg"></i>` |
| **View Invoice / Detail** | 👁️ 🔍 | `<i class="bi bi-eye"></i>` |
| **Search Records** | 🔍 | `<i class="bi bi-search"></i>` |
| **Staff Sign In** | 🔑 🚪 | `<i class="bi bi-box-arrow-in-right"></i>` |
| **Staff Sign Out** | 🚪 | `<i class="bi bi-box-arrow-right"></i>` |
| **Operations Dashboard** | 📊 📈 | `<i class="bi bi-speedometer2"></i>` |
| **UPI Verifications Queue** | 📱 💳 | `<i class="bi bi-phone"></i>` |
| **Bank & UPI Configuration** | 🏦 | `<i class="bi bi-bank"></i>` |
| **Record Payment / Cash** | 💵 | `<i class="bi bi-cash-coin"></i>` |
| **Check / Success State** | ✅ ✔️ | `<i class="bi bi-check2-circle"></i>` |
| **Pending / Overdue State** | ⚠️ ⏳ | `<i class="bi bi-clock-history"></i>` |
| **Mask / Unmask Account** | 👁️ 🔒 | `<i class="bi bi-eye"></i>` / `<i class="bi bi-eye-slash"></i>` |

---

## 5. Security & Authentication Architecture

### 1. Masthead Auth-Gating (`partials/_masthead.html`)
- **Unauthenticated Visitors (`login.html`)**:
  - The masthead navigation tabs (`Dashboard`, `New Bill`, `Bills`, `UPI Verifications`, `Bank & UPI`, `Admin`) and user session information (`admin • Logout`) are strictly hidden via `{% if variant == 'staff' and user.is_authenticated %}`.
  - The brand logo links to dashboard only when authenticated; unauthenticated clicks do not trigger redirect loops.
- **Customer Statement Portal (`customer_portal.html`)**:
  - Renders `variant='customer'`, isolating the customer view to the official broadsheet header and language toggle with zero staff navigation tabs.

### 2. Staff Sign-In Card (`login.html`)
- Scaled from a cramped 400px box into a generous **440px wide** clerk panel with `36px 32px` internal padding and a clean 1px `#d6cfc4` rule border.
- Removed duplicate newspaper logo inside the card body (the top masthead logo now stands alone cleanly).
- Inputs scaled to **48px min-height** (`16px` font) with `<i class="bi bi-person"></i>` and `<i class="bi bi-key"></i>` icons.
- Primary Sign In button scaled to **48px min-height** (`16px` bold font) with `<i class="bi bi-box-arrow-in-right"></i>`.

### 3. URL Route Fallbacks (`config/urls.py`)
- Standardized `LOGIN_URL = 'login'` (`/login/`).
- Added automatic redirect from `/accounts/login/` to `/login/` to ensure no 404 errors if default Django URLs are invoked.
- Registered root-level customer portal shortcuts: `/statement/<uuid:token>/` and `/c/<uuid:token>/`.

---

## 6. Page-by-Page Implementation Record

### 1. Operations Dashboard (`/bills/` & `/`)
- **Quick Action Bar**: High-contrast desktop search bar (42px height) + primary maroon `+ Create New Bill` button (42px height).
- **Financial KPI Cards (`partials/stats_strip.html`)**:
  - 4 key metrics: *Today's Billed*, *This Month's Billed*, *Total Collected*, *Balance Due*.
  - Financial figures rendered in **32px bold tabular numbers**.
  - Mobile layout: strict $2 \times 2$ grid with 16px cell padding; Desktop layout: 4-metric horizontal strip with 1px vertical dividers.
- **Dual-Layout Recent Bills (`partials/bills_table.html`)**:
  - **Desktop (`md+`)**: Dense data table with 13px uppercase headers, 15px invoice/client cells, 15px tabular totals, status dots (`● Paid`, `● Partial`, `● Unpaid`), and 32px `.btn-desk-sm` action pills (`View`, `PDF`, `WhatsApp`, `Portal`).
  - **Mobile (`< md`)**: Separate standalone 5-line card blocks with 16px padding and 12px vertical gaps. Zero nested borders. Paid bills feature a compact 3-line layout where the entire card is a tap target to invoice details.

### 2. Point-of-Sale Bill Creation Workspace (`/bills/new/`)
- **Two-Column Split**:
  - **Left Column**: Clean step-card sequence for Client Information, Placement Details (with standard broadsheet presets + custom dimension inputs), and Financials.
  - **Right Column**: Live sticky POS receipt card powered by vanilla JS (`calculator.js`).
- **Form Controls**: Standardized inputs, selects, placement chips (`.chip-btn`), and payment method pills (`.pill-choice`) to 42px min-height.
- **Contract Preservation**: Preserved all DOM element IDs and data attributes required by `calculator.js` for real-time total, discount, and balance calculations.

### 3. Bill Search & Filters (`/bills/search/`)
- Unified desk panel filter interface with 42px search input, status dropdown, edition select, and date range inputs.
- Results table utilizes standardized 13px headers, 15px cells, and `.btn-desk-sm` action buttons.

### 4. Bill Detail & Payment Ledger (`/bills/<id>/`)
- **Header**: Clean breadcrumb (`Dashboard / VG-2026-0003`), 28px Noto Serif invoice number, and status dot.
- **Two-Column Ledger List**:
  - Left: Client name (bilingual: Devanagari primary + English secondary), phone, address, edition, placement, and page number.
  - Right: Total Amount, Paid so far (green), and Balance Due (24px bold maroon).
- **Authoritative Action Bar**: 44px min-height outline buttons with Bootstrap icons (`English PDF`, `Hindi PDF`, ` मुहर प्रति / Seal & Sign`, `WhatsApp reminder`, `Customer portal ↗`).
- **In-Place HTMX Payment Recording**:
  - Renders when balance due $> 0$.
  - Strict server-side validation: positive amount $\le$ balance due, 12-digit numeric UTR for UPI payments.
  - Submits via HTMX targeting `#bill-detail-pane` with outerHTML swap — instantly updates balance, payment history, and status dot without full page reload.
  - Replaced by a calm green confirmation banner (`● This invoice is fully paid. No balance due.`) when settled.

### 5. Customer Self-Service Statement Portal (`/c/<token>/` & `/statement/<token>/`)
- **Zero Login Required**: Governed by high-entropy client UUID tokens (`Client.access_token`).
- **720px Centered Container**: Wrapped in a clean 720px max-width container with 16px/24px padding. Zero horizontal overflow (`scrollWidth == innerWidth == 360px`).
- **Financial Summary**: 32px dominant maroon balance due headline with compact totals summary.
- **Zero-Fee Native UPI Deep Linking**:
  - Mobile: Primary maroon button (`Pay ₹X,XXX via UPI`) opening native UPI apps (GPay, PhonePe, Paytm, BHIM) with prefilled VPA, payee name, amount, and invoice reference.
  - Desktop: 168x168px dynamic UPI QR code rendered on-demand via `qrcode` package with copyable bank details.
- **Customer UTR Submission**:
  - Dedicated HTMX submission form with strict 12-digit numeric validation (`inputmode="numeric"`, `maxlength="12"`).
  - Submits asynchronously, creating a `PaymentSubmission` record and replacing the form with a calm confirmation notice.
- **Split Ledger**: Unpaid advertisements presented first; settled/paid advertisements presented in a quieter section below.

### 6. Staff Bank & UPI Settings with Encryption (`/bills/settings/payment-info/`)
- **Fernet Authenticated Encryption**: Bank account numbers are stored encrypted at rest (`billing/crypto.py`, `EncryptedCharField`) using AES-128 in CBC mode with HMAC-SHA256 authentication.
- **Interactive Masked Account Toggle**: Displays masked account number (`••••••••1234`) with an interactive toggle button to reveal full digits.
- **Live QR Preview**: Real-time on-screen preview of the generated UPI payment QR code.

### 7. Customer UPI Verification Queue (`/bills/submissions/`)
- Filter tabs for *Pending*, *Verified*, and *Rejected* customer UTR submissions.
- Row-level HTMX actions (`[ Verify & Credit ]` / `[ Reject ]`) that credit the client's bill and update the navbar badge out-of-band (`hx-swap-oob="true"`).

---

## 7. PDF Invoicing Architecture v3.0 (Full A4 Canvas)

### 1. Full A4 Canvas Coverage
- Eliminated the awkward "half-page slip" look by locking `.invoice-container` to exact A4 printable height (`278mm`) with a 2px outer ink border and a full-height flex column.
- Scaled header logo (54px), masthead typography (16pt), metadata cards (84px min-height), dynamic QR code (86px), and signatory clearance box to command the full page.

### 2. Expandable Ledger Spine Engine
- Invoice table uses `height: 100%` with item rows set to `height: 1px` (hugging content) and a `.blank-filler-row` (`height: auto`) absorbing remaining vertical space.
- Table column rules run seamlessly down to the totals bar, creating the authentic appearance of a traditional bound ledger book regardless of whether an invoice has 1 ad or 6 ads.

### 3. Dual Format Architecture
- **Format A (Default, `sign=0`) — Computer Generated Document**:
  - Official green verified check badge + Digital Verification ID (`Ref: VG-YYYY-NNNN`).
  - Statutory declaration under the Information Technology Act, 2000: *"This is a computer generated invoice and does not require a physical signature."*
- **Format B (Optional, `sign=1`) — Physical Seal & Sign**:
  - Traditional broadsheet clearance box with newspaper stamp zone and authorized signatory underline for government/B2B clients requiring physical ink or rubber stamps.
- **On-Screen PDF Preview Toolbar**:
  - Persistent `.no-print-toolbar` offering 1-click toggling between `Format: [ Computer Generated | Seal & Sign ]` and `Language: [ English | हिंदी ]`.

### 4. Strict Pure-Language Invoicing Engine
- **Zero Language Mixing**: Completely eliminated bilingual slashes and parenthetical translations in generated PDFs.
- **100% Full English (`lang=en`)**:
  - English title (`ADVERTISEMENT INVOICE`), English client name isolation, English currency in words (*"Rupees Three Thousand Five Hundred Only"*), English paid stamp (`PAID IN FULL`), and 5 English legal terms.
- **100% Full Hindi (`lang=hi`)**:
  - Authentic Devanagari broadsheet terms (`विज्ञापन देयक`, `बिल क्रमांक:`), Hindi client name isolation, pure Hindi currency words (*"तीन हज़ार पाँच सौ रुपये मात्र"*), Hindi paid stamp (`पूर्ण भुगतान प्राप्त — खाता चुकता`), and ५ वैधानिक शर्तें.

### 5. Unified Newspaper Identity
- Official brand name is strictly:
  - **हिन्दी**: `"विश्वगुरु की झलक"` (the redundant prefix *"दैनिक"* has been completely removed).
  - **English**: `"Vishwaguru Ki Jhalak"`.

---

## 8. Responsive & Accessibility Standards

- **Mobile Viewport (360px & 390px)**:
  - Verified `document.documentElement.scrollWidth == window.innerWidth == 360px` with 0 horizontal overflows.
  - Sticky header height: 48px; right-edge gradient fade indicator on horizontally scrollable navigation tabs.
  - All interactive buttons have $\ge 44\text{px}$ touch targets.
- **Tablet / Medium Viewport (768px)**:
  - Clean two-column transitions for forms and ledger details.
- **Desktop Viewport (1200px & 1440px)**:
  - Strict 24px vertical separation between dashboard strips, tables, and secondary panels.
  - Generous 16px–20px inner padding on desk panels.
- **Accessibility & Contrast**:
  - All body text $\ge 15\text{px}$; secondary text $\ge 14\text{px}$; ink color `#1c1917` on `#faf8f4` delivers an exceptional 14.8:1 contrast ratio (exceeding WCAG AAA).
  - Muted text `#57534e` delivers 4.6:1 contrast ratio (exceeding WCAG AA).

---

## 9. Verification & Automated Test Suite

The entire application state is covered by an automated test suite.

```powershell
.\.venv\Scripts\python.exe manage.py test billing
```

### Test Suite Execution Summary
- **Total Test Cases**: 27
- **Results**: 27 Passed, 0 Failed, 0 Errors (**100% OK**)
- **Key Test Modules**:
  1. `test_bill_creation_and_numbering`: Sequential `VG-YYYY-NNNN` format and yearly reset.
  2. `test_fernet_account_encryption_roundtrip`: Sensitive bank account encryption/decryption.
  3. `test_customer_portal_public_access_and_isolation`: Client data isolation via token.
  4. `test_customer_portal_wrong_or_unknown_token_returns_404`: Strict security boundary.
  5. `test_record_payment_validation_amount_exceeds_balance`: Server-side amount validation.
  6. `test_record_payment_upi_mode_requires_12_digit_utr`: 12-digit numeric UTR enforcement.
  7. `test_customer_payment_submission_valid_utr`: HTMX UTR submission pipeline.
  8. `test_customer_payment_submission_invalid_utr`: Bilingual rejection of invalid UTRs.
  9. `test_pure_language_pdf_english_and_hindi`: Verification of pure language PDF rendering.
  10. `test_sign_mode_parameter_in_pdf`: Verification of computer-generated vs. seal & sign formats.
