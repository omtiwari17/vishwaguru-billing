# GEMINI.md — Agent Working Guidelines & Project Context

> [!IMPORTANT]
> **MANDATORY RULES FOR ALL AGENTS WORKING ON THIS REPOSITORY:**
> 1. **READ FIRST:** Always read this file (`GEMINI.md`) before taking any action or making any changes.
> 2. **ALWAYS UPDATE:** Keep this file updated with current progress, architectural decisions, and context at every step.
> 3. **DO NOT COMMIT:** Do **NOT** run `git commit` until the user explicitly instructs you to commit.
> 4. **NEVER PUSH:** **NEVER run `git push`**. Pushing to remote is strictly prohibited unless explicitly requested by the user.
> 5. **DEV SERVER PORT:** The local development server runs on port **`8080`** (`http://127.0.0.1:8080/`).

---

## 1. Project Overview
* **Name:** `vishwaguru-billing`
* **Purpose:** Internal ad billing, tracking, and bilingual PDF generation system for **Vishwaguru Ki Jhalak**. Replaces manual billing with instant PDF generation, payment tracking, and a searchable bill database.
* **Repository:** `https://github.com/omtiwari17/vishwaguru-billing` (Flat root structure, no subfolders).

---

## 2. Tech Stack & Architecture
* **Backend:** Python 3.11 / Django 5.1 (monolithic, server-rendered).
* **Database:** 
  * Development: SQLite (`db.sqlite3`).
  * Production: PostgreSQL (self-hosted locally on an Ubuntu/Debian PC).
* **PDF Engine:** WeasyPrint (HTML/CSS to PDF live on demand; **zero stored PDF files on disk**), with browser print fallback.
* **Frontend:** Django Templates + Vanilla JavaScript for live total calculation (`calculator.js`), Google Fonts (*Noto Sans Devanagari* + *Inter*).
* **Language Support:**
  * **Site UI:** Simple English by default, with a 1-click **`[ English | हिंदी ]`** language switcher toggle in the top navbar.
  * **Bill Invoicing:** Selectable between **English**, **हिंदी**, or **Bilingual (हिंदी + English)** on the creation form.
  * **PDF & Print:** Dedicated buttons on bill details screen to download/view in **English PDF**, **हिंदी PDF**, or **Bilingual PDF**.
* **Deployment & Networking:**
  * Production PC: Ubuntu/Debian Linux.
  * Web Server: Gunicorn WSGI behind Nginx reverse proxy.
  * Remote Access: Cloudflare Tunnel (`cloudflared`) for secure HTTPS without port forwarding.
  * Process Management: `systemd` service units for Django and `cloudflared` (auto-start on boot/reboot).
  * Automated Backups: Periodic `pg_dump` cron script.

---

## 3. Finalized Business & Design Rules (Aligned via `/grill-me`)

1. **Ad Placements & Pricing:**
   - Standard presets dropdown (`PlacementType`):
     - Front Page — Full Page / मुख्य पृष्ठ - पूरा पेज
     - Front Page — Half Page / मुख्य पृष्ठ - आधा पेज
     - Front Page — Quarter / मुख्य पृष्ठ - चौथाई
     - Inside Page — Full / Half / Quarter / अंदर का पृष्ठ
     - Back Page / अंतिम पृष्ठ
     - Ear Panel / शीर्ष विज्ञापन (ईयर पैनल)
     - Custom Size / अन्य विशिष्ट आकार
   - When "Custom Size" is selected, staff can enter custom dimensions.
   - Staff can enter or adjust the rate/base amount for any selection.
   - **Taxes:** No GST calculations (all amounts are all-inclusive flat totals).
   - **Discount:** Optional discount field (`discount_amount`), subtracted from `base_amount` to give `total_amount = base_amount - discount_amount`.

2. **Bill Numbering:**
   - Auto-generated sequential format: `VG-YYYY-NNNN` (e.g. `VG-2026-0001`).
   - Resets to `0001` each calendar year.

3. **Client Information:**
   - `client_name` (Required)
   - `client_phone` (Optional — used for payment follow-ups & 1-click WhatsApp sharing; if omitted, bills can still be created and WhatsApp share button opens recipient chooser)
   - `client_address` (Optional)
   - `client_gstin` (Optional PAN / GSTIN reference for B2B clients)

4. **Epaper Verification:**
   - `epaper_link` (URL to the online publication/post)
   - `page_number` (e.g. "Page 1", "Page 4")
   - Both displayed clearly on the generated invoice and bill detail screen.

5. **Payment Tracking & Info:**
   - `PaymentInfo` (Singleton table): Newspaper's bank name, account number, IFSC, UPI ID, account holder name, phone, and address.
   - Per-bill status: `Unpaid`, `Paid`, `Partial` (with `amount_paid`, `payment_method`, `payment_note`).
   - Actual payments happen outside the system (Cash, UPI, NEFT, Cheque); tracked manually by staff.

6. **PDF Invoicing Features:**
   - Official "विश्वगुरु की झलक" logo image header from static folder.
   - Dynamic UPI QR Code generated on-demand via `qrcode` package (`upi://pay?pa={upi_id}&pn=Vishwaguru&am={total_amount}&tn={bbill_number}`).
   - Amount in words auto-rendered in Hindi and/or English.

7. **UI / UX Features:**
   - Single-screen bill creation with live total calculation (vanilla JS).
   - 1-Click "Share on WhatsApp" button on bill details screen (`https://wa.me/{phone}?text=...`) formatted in the chosen bill language.
   - Search & filter past bills by client name, phone, bill number, or date range.
   - **STRICT ICON SYSTEM (NO EMOJIS)**: Strictly use vector **Bootstrap Icons** (`<i class="bi bi-..."></i>`). **Never use Unicode emojis** in templates or UI controls. All buttons, labels, actions, and tabs must use proper Bootstrap Icons.

---

## 4. Current Repository State
* **Documentation files:** `HLD.md`, `LLD.md`, `PROJECT_CONTEXT.md`, `REQUIREMENTS.md`, `README.md`, `GEMINI.md`.
* **Git configuration:** `.gitignore` configured for Django, `.env`, SQLite, virtual environments.
* **Active branch:** `main` (features merged and verified).
* **Code status: Operations Dashboard, Field-Level Encryption & Customer Statement Portal Integrated.**
  - Django project (`config`) and billing app (`billing`) active on port 8080.
  - Models (`Bill`, `PaymentInfo`, `Client`, `PaymentSubmission`) fully migrated.
  - All 20 automated unit tests passed (100% OK).
  - **Dedicated Operations Dashboard (`/bills/` & `/`)**:
    - Post-login landing page now redirects straight to the Dashboard (`LOGIN_REDIRECT_URL = 'billing:dashboard'`).
    - Top Quick Action Hero with buttons: **[ + Create New Bill ]**, **[ 🔍 Search Bills ]**, and **[ 📱 UPI Verifications ]**.
    - 4 Financial KPI cards: Today's Billed / Collected, This Month's Billed / Collected, Total All-time Collections, and Total Outstanding Balance Due (कुल बकाया).
    - Real-time Alert Banner for customer-submitted UPI payments pending staff verification.
    - Recent Advertisement Invoices table (10 latest bills) with 1-click action buttons (View, Download PDF, WhatsApp share, Customer Portal link).
    - Payment Status Overview with visual progress bars (Fully Paid, Partial Paid, Unpaid).
    - Top Outstanding Clients (overdue follow-up) list with 1-click WhatsApp payment reminders and direct ledger links.
    - Official newspaper bank details and UPI ID preview with 1-click edit link.
    - Updated navbar with dedicated Dashboard link (`bi-speedometer2`).
  - **Customer Self-Service Statement Portal (`/statement/<uuid:token>/` & `/c/<uuid:token>/`)**:
    - Secure, unguessable UUID token per client (`Client.access_token`) — zero login required for clients.
    - Mobile-first, bilingual statement view (`[ English | हिन्दी ]`).
    - 4 Financial Ledger Summary Cards: Total Ads Published, Total Billed, Total Paid, and Outstanding Balance Due (कुल शेष बकाया).
    - Distinct ledger sections: Unpaid/Pending Advertisements vs. Cleared/Paid in Full History.
    - Public bill PDF download directly from statement portal without staff credentials (`/statement/<token>/bill/<id>/pdf/`).
    - 1-click verification of online published ads via e-paper link.
  - **Zero-Fee Native UPI Payment Integration**:
    - Deep-linking (`upi://pay?pa=...&pn=...&am=...&tn=...&cu=INR`) opens the customer UPI app with a prefilled amount.
    - Zero intermediary transaction fees, 100% direct settlement.
    - Dynamic UPI QR Code for desktop/tablet scanning.
    - Bank details with copy buttons and individual bill or total balance payment links.
  - **Customer UTR Submission & Staff Verification Flow**:
    - Customers submit a 12-digit UTR directly on the statement page.
    - Creates `PaymentSubmission` records and shows pending verification alerts.
    - Staff dashboard and bill detail pages offer instant verification and payment confirmation.
  - **Staff Sharing & Management**:
    - 1-click WhatsApp statement sharing and direct portal preview links.
    - Navigation link to UPI verification queue in the top navbar.
  - **Staff Bank & UPI Settings & Field-Level Encryption (`/bills/settings/payment-info/`)**:
    - Staff UI to view, update, and manage official newspaper bank details, IFSC, and UPI ID directly from the portal (no raw Django admin needed).
    - Interactive masked account-number toggle (`••••••••1234`) and live QR preview.
    - **Encryption at Rest:** Sensitive bank account numbers are stored via Fernet authenticated symmetric encryption (`billing/crypto.py`, `EncryptedCharField`) while transparently decrypting in Python for UI and PDFs.

---

## 5. Development & Testing Commands
* Run development server:
  ```powershell
  .\.venv\Scripts\python.exe manage.py runserver 8080
  ```
* Run automated test suite:
  ```powershell
  .\.venv\Scripts\python.exe manage.py test billing
  ```
* Seed demo data & admin user:
  ```powershell
  .\.venv\Scripts\python.exe manage.py seed_data
  ```

---

## 6. Current Status & Next Steps
* **UI/UX Comprehensive Restyle — Phase 1 (Foundation Fixes Complete)**:
  - Added Bootstrap Icons CDN to billing/templates/billing/base.html for icon rendering across forms.
  - Removed duplicate URL routes in billing/urls.py (submissions/ and verify/ duplicate patterns).
  - Cleaned up duplicate imports in billing/forms.py (PAYMENT_METHOD_CHOICES_HI, BILL_LANG_CHOICES_HI, PaymentSubmission).
  - Expanded billing/static/billing/css/style.css with newspaper-office compliant component classes adhering strictly to max 4px radius, 1px rules, zero shadows, zero gradients, and Mukta typography.
  - Automated test suite verified: 25/25 automated unit tests passing (100% OK).
* **UI/UX Comprehensive Restyle — Phase 2 (5 Pages Restyled & Unified)**:
  - login.html: Branded newspaper-office login card, zero shadows, clean Mukta & Noto Serif typography, bilingual error messages.
  - bill_form.html: Fully unified 2-column POS workspace with clean step cards, 4px radii, placement chips, payment pills, and live sticky receipt with preserved calculator.js DOM/ID contracts.
  - bill_search.html: Restyled with desk-panel, data-table, status-dot.html, btn-desk-*, and Indian currency formatting with zero undefined CSS variables.
  - payment_info_settings.html: Restyled into a calm 2-column desk panel with masked account toggle, live QR test card, and 4px radii.
  - payment_submissions_list.html: Rewritten to properly inherit from billing/base.html, using the shared masthead, clean status filter tabs, and desk-table.
  - All 25/25 automated unit tests passing (100% OK).
* **Current Status & Next Steps**:
  - All staff-facing pages, portal, and shared layouts now 100% conform to the newspaper-office design system.
  - Dev server active and ready for visual clerk operations.
* Merged `feature/customer-statement-portal` into `main`.
* Automated test suite: 20/20 tests passing (including encryption roundtrip & settings view tests).
* Dev server running on `http://127.0.0.1:8080/`.
* Ready for user review or further instructions.
* **Newspaper-Office Design System Restyling (Django + HTMX + Tailwind v4)**:
  - **Core Aesthetic:** Calm, dense clerk desk tool. Paper (`#faf8f4`), ink (`#1c1917`), muted (`#78716c`), rule (`#e7e2d9`), maroon (`#9f1d1d`), paid green (`#15803d`), partial amber (`#b45309`).
  - **Typography:** `Mukta` for all UI text (Latin + Devanagari match), `Noto Serif Devanagari` only for the masthead and page titles. Weights: 400, 500, 600 only. `tabular-nums` on every single amount.
  - **Shape:** 4px radius max, 1px borders, zero shadows, zero gradients, zero nested cards.
  - **Status:** Coloured dot + text (`● Paid`, `● Partial`, `● Unpaid`). No pastel pill badges.
  - **Shared Template Partials (`billing/templates/billing/partials/`):**
    - `upi_badge.html`: Navbar UPI verification count badge (supports out-of-band HTMX swap).
    - `upi_alert.html`: Calm, understated customer UPI payment alert banner.
    - `stats_strip.html`: 4-metric strip with vertical dividers (Today's Billed, Month, Total Collections, Balance Due).
    - `bills_table.html`: Dense bills table with tabular-nums, bilingual client & placement details, and clerk actions.
    - `status_dot.html`: Coloured dot + plain status text.
    - `submission_row_verified.html`: Row-level vverify/reject feedback with OOB navbar badge swap.
  - **HTMX Enhancements:**
    - Live search in bills table via HTMX debounce without full page reload.
    - Row-level vverify/reject actions for customer UPI submissions.
    - Out-of-band updates (`hx-swap-oob="true"`) for the navbar pending verification count badge.
  - **Phase 1 Complete:** `base.html` and `dashboard.html` fully restyled and verified against test suite (20/20 OK) and visual rendering.
  - **Phase 2 Polish Complete:**
    - Dual Layout in `partials/bills_table.html`: dense tabular view on `md+` (`hidden md:block`) and stacked cards on small screens (`block md:hidden`).
    - Stacked card layout: Line 1 = Invoice no + date + status dot; Line 2 = Client name + phone; Line 3 = Placement & edition; Line 4 = Total amount + Balance due.
    - Actions on mobile: Visible primary green WhatsApp button ($\ge 44\text{px}$ touch target) + clerk `...` `<details>` menu containing View invoice, Download PDF, and Statement portal links (each $\ge 44\text{px}$).
    - Stats Strip: $2\times 2$ grid with 1px dividers on mobile, 4-metric horizontal divider strip on desktop, increased cell padding, and 24px vertical separation before the bills panel.
    - Indian Currency Filter: `indian_currency` filter in `billing/templatetags/billing_tags.py` (`₹1,84,200` without `.00` unless paise exist).
    - Authentic Pluralization: `bbill_noun` & `bbill_count_label` filters for English ("1 bill" vs. "2 bills") and Hindi ("1 बिल" vs. "2 बिल", "1 ग्राहक का भुगतान" vs. "N ग्राहकों के भुगतान").
    - Unified Newspaper Identity: "विश्वगुरु की झलक" in Hindi and "Vishwaguru Ki Jhalak" in English across masthead, titles, and footer.
    - Removed "Server: port 8080" footer and removed the redundant Bank & UPI panel from the dashboard (kept in secondary panels: Payment Status + Overdue Accounts).
    - Darkened muted text to `#57534e` for WCAG AA compliance; body text $\ge 14\text{px}$.
    - HTMX live search operates synchronously across both desktop table and mobile stacked list views.
    - Verified with CDP screenshots across 360px, 390px, 800px, and 1200px viewports in both English and Hindi. Automated test suite: 20/20 passing.
  - **Phase 3 Mobile Hierarchy Refinement Complete (< md)**:
    - **Header**: Single compact row containing small official logo + newspaper title on left, EN/हिन्दी toggle on right. Subtitle hidden on mobile (`hidden md:block`); `admin • Logout` moved to footer on mobile (`block md:hidden`). Horizontally scrollable nav tabs with zero clipping.
    - **Stats Strip**: Strict $2\times 2$ grid on mobile with 16px cell padding, 12px muted label, and 22px bold tabular amount.
    - **Recent Bills Panel Header**: Full-width search input + full-width primary maroon `+ Create New Bill` button. Large "View all" removed from top on mobile and placed as a small text link at the bottom of the bills list.
    - **Separate Bill Card Blocks**: 16px padding, 1px border (`#e7e2d9`), 12px gap between blocks, with 16px padding from screen edge everywhere (no touching screen boundary, zero nested card borders).
    - **Exact 5-Line Card Hierarchy**:
      - Line 1: `Invoice no · Date` (small muted text) on left, `● Status dot + text` on right.
      - Line 2: `Client name` (16px, weight 500) on left, `Total amount` (16px, weight 600, `tabular-nums`) on right.
      - Line 3: `Secondary English client name` (small muted text) on left; `Due ₹X,XXX` in maroon on right only when balance due > 0 (omitted when paid).
      - Line 4: Placement details in single chosen language, single line, truncated.
      - Line 5: Actions: Small outline `[ WhatsApp ]` button (only when balance due > 0) + `[ ⋯ ]` menu button ($\ge 44\text{px}$ tap target). No solid green buttons. No phone numbers cluttering the card.
    - Desktop layout (`md+` / $\ge 768\text{px}$) and business logic remain completely untouched. Automated test suite: 20/20 passing.
  - **Phase 4 Mobile Polish & Clerk Refinements Complete (< md)**:
    - **Paid Bill Cards**: Empty action row and divider completely eliminated. Whole card converted into a clickable link to invoice details (`/bills/<id>/`) via stretched link. `[ ⋯ ]` menu placed on Line 1 top-right alongside the `● Paid` status dot. Card height reduced by ~40%, providing immediate visual contrast between settled and outstanding invoices.
    - **Stats Strip at 360px**: Label in Cell 3 shortened to `"Collected"` (Hindi: `"कुल प्राप्त"`). Enforced fixed label heights (`h-[16px]`) and vertical centering across all 4 metric cells, eliminating row misalignment across narrow screens.
    - **Search & Create Header**: Removed the outer card wrapper/border on mobile so the search bar and `+ Create New Bill` button sit cleanly directly on the `#faf8f4` paper background. Search placeholder set to `"Search bills"` (Hindi: `"बिल खोजें"`).
    - **WhatsApp Reminder Button**: Widened to fill available row space (`flex-1`) alongside the 44px `[ ⋯ ]` menu button. Labeled `"WhatsApp reminder"` (Hindi: `"व्हाट्सऐप तगादा"`) with $\ge 44\text{px}$ minimum tap target.
    - **Navigation Tabs**: Added right-edge gradient fade overlay (`bg-gradient-to-l from-white to-transparent`) indicating horizontal scrollability on mobile screens.
    - **Bilingual Page Translations**: Custom `format_page` filter accurately renders `"Page X"` $\to$ `"पृष्ठ X"` across both desktop and mobile views. Verified masthead identity `"विश्वगुरु की झलक"` and Hindi subtitles.
    - **Verification**: Verified across 360px, 390px, 800px, and 1200px viewports in both English and Hindi. Automated test suite: 20/20 tests passing (100% OK).
  - **Desktop Spacing & Mobile Scoping Fixes**:
    - **Vertical Gaps**: Restored strict 24px vertical separation between Stats Strip -> Bills Panel and Bills Panel -> Secondary Panels on desktop (md+), as well as between Stats Strip -> 'Recent bills' heading on mobile.
    - **Bills Panel Enclosure & Padding**: Restored 1px border (var(--rule)) and 16-20px inner padding on desktop (padding: 16px 20px), ensuring heading, search, buttons, and table rows do not touch the panel borders.
    - **Unboxed Mobile Scoping**: Scoped transparent/unbordered styling strictly to < md, preserving clean standalone card blocks on mobile while ensuring a crisp, enclosed clerk panel on desktop.
    - **Verification**: Re-captured and validated across 360px, 390px, and 1200px viewports in both English and Hindi. Automated test suite: 20/20 passing.
  - **Customer Statement Portal Restyling (`customer_portal.html`)**:
    - **Visual & Layout Alignment**: Adheres strictly to the calm clerk newspaper-office design system (`#faf8f4` paper background, Mukta typography, Noto Serif Devanagari titles, 4px max radius, 1px `#e7e2d9` borders, zero shadows, maroon for primary action only).
    - **7-Tier Mobile-First Layout Hierarchy**:
      1. Compact masthead header (`विश्वगुरु की झलक` / `Vishwaguru Ki Jhalak`) + `[ EN | हिन्दी ]` toggle. Completely removed staff nav tabs and `admin/Logout`.
      2. Bilingual client name (e.g. `पटेल ऑटोमोबाइल्स` / `Patel Automobiles`) + single date line (`Statement • 28 Oct 2026` / `खाता विवरण • 28 Oct 2026`).
      3. Balance Due: Single dominant 32px maroon headline (`₹3,500`) with compact summary (`Total billed ₹7,000 • Total paid ₹3,500 • 2 ads`). Eliminated 4-card grid.
      4. Primary Action: Full-width maroon button (`Pay ₹X,XXX via UPI` / `यूपीआई द्वारा ₹X,XXX भुगतान करें`) opening the native UPI app via `upi://` deep-link with prefilled amounts and notes.
      5. Desktop-Only Dynamic QR: UPI QR code renders strictly on desktop (`hidden md:block`), completely hidden on mobile phones.
      6. Secondary Action & HTMX UTR Submission: Outline button (`I have paid, submit UTR ↓` / `भुगतान कर दिया? यूटीआर दर्ज करें ↓`) expanding a dedicated 12-digit UTR input form (`partials/utr_form.html`). Submission validates via HTMX without full page reload and replaces with a calm confirmation notice (`partials/utr_submitted.html`).
      7. Collapsible Bank Details: Native `<details>` accordion (`Bank transfer details (NEFT / RTGS)`) with 1-click clipboard copy buttons for Account Number, IFSC, and Bank Branch.
      8. Split Bills Ledger: Unpaid advertisements displayed first (with date, placement, edition, page number, total, balance due, and PDF/epaper links); settled/paid bills listed below in a separate quieter block.
    - **Token Security & Client Isolation**: Enforced strict client scoping via `access_token` UUID; verified via new automated test `test_customer_portal_wrong_or_unknown_token_returns_404` guaranteeing non-existent or forged tokens return 404 and leak zero client ledger data.
    - **Verification**: Verified via Playwright CDP screenshots at 360px and 1200px across both English and Hindi. Automated test suite: 21/21 tests passing (100% OK).
    - **Customer Statement Portal Layout & Verification Polish**:
      - **720px Centered Container**: Wrapped header, main content, and footer in a unified centered container (`max-width: 720px; margin: auto;`) with 16px side padding on mobile (`px-4`) and 24px on desktop (`md:px-6`).
      - **Zero Horizontal Overflow at 360px**: Verified `document.documentElement.scrollWidth == window.innerWidth == 360px` with 0 overflows. Header logo + masthead and EN/हिन्दी toggle fit with room to spare without clipping.
      - **Header Spacing**: Enforced exact 24px vertical separation between the bottom of the sticky header and the client name `<h1>`, preventing any overlap.
      - **Strict 12-Digit Numeric UTR Validation**: HTML input attributes (`inputmode="numeric"`, `maxlength="12"`, `pattern="[0-9]{12}"`) with strict server-side regex (`clean_utr_number`) rejecting non-numeric/wrong-length inputs with clear bilingual inline errors (`"यूटीआर संख्या ठीक 12 अंकों की होनी चाहिए (केवल 0-9)।"` / `"UTR number must be exactly 12 digits (numeric only)."`). Updated test suite to verify HTMX error responses.
      - **Device-Specific UPI Action**: The "Pay via UPI" deep-link button displays strictly on mobile (`md:hidden`). On desktop (`md+`), only the dynamic QR code with the UPI ID and the "I have paid, submit UTR" button are shown.
      - **Plain Link Labels**: Renamed "Epaper link" / "ई-पेपर लिंक" to plain clerk label "View ad" / "विज्ञापन देखें".
      - **Shared Masthead Partial (`partials/_masthead.html`)**:
        - Unified header component shared across `base.html` (`variant='staff'`) and `customer_portal.html` (`variant='customer'`).
        - Logo (24px height), newspaper title (Noto Serif Devanagari 600, 1.35rem on desktop / 0.95rem on mobile), padding (10px 0 on desktop / 8px 0 on mobile), 1px bottom rule, and EN/हिन्दी toggle are pixel-for-pixel identical.
        - Staff variant adds: admin/Logout and horizontal nav tabs. Subtitle removed to allow logo to stand alone cleanly.
        - Customer variant: clean masthead and language toggle only. No subtitle row, zero staff nav. Aligns to 720px container.
      - **Portal Desktop QR Code Polish**: 168x168px centered QR code with 8px margin above the caption and generous container padding (20px 24px) ensuring the caption never touches box borders.
      - **Header Paper Background & Chevron Arrow Polish**:
        - Set header background to paper `#faf8f4` (with 1px rule `#e7e2d9`), eliminating the white band and matching the seamless paper aesthetic.
        - Replaced character arrows ("↓" and VS-15 hacks) with clean 16px inline SVG chevrons (`stroke="currentColor"`, `stroke-width="2"`, no fill) matching the surrounding `#1c1917` ink text color across EN and HI at 360px and 1200px.
        - Configured smooth 180deg rotation when sections expand (`details[open]` / `aria-expanded="true"`).
      - **Verification**: Verified via Playwright CDP metrics and screenshots at 360px and 1200px across both English and Hindi. Automated test suite: 21/21 tests passing (100% OK).
  - **Bill Detail Page Restyling (`bbill_detail.html` & `partials/bbill_detail_pane.html`)**:
    - **Visual & Layout Alignment**: Adheres strictly to the calm clerk newspaper-office design system (`#faf8f4` paper background, Mukta typography, Noto Serif Devanagari titles, 4px max radius, 1px `#e7e2d9` borders, zero shadows, maroon for primary action only). Mobile-first.
    - **Removed All Legacy Prototype Elements**: Completely eliminated Bootstrap icons (`<i class="bi ...">`), neon yellow cards, pastel badges, and gradient styling.
    - **6-Part Page Architecture**:
      1. **Breadcrumb & Title**: Clean breadcrumb (`Dashboard / VG-2026-0002` linking to `/bills/`), large invoice title (`VG-2026-0002`) with status dot component (`● Paid`, `● Partial`, `● Unpaid`), and creation timestamp.
      2. **Plain Two-Column List (No Cards Inside Cards)**:
         - Left Column: Client (bilingual: primary Devanagari + secondary English, clickable `tel:` phone, address, GSTIN/PAN), Edition & Date, Placement & Page (`Inside Page — Quarter · Page 4` with custom size and "View ad ↗" link).
         - Right Column: Total Amount (`tabular-nums`, with discount/previous due noted), Paid So Far (paid green), and Balance Due (`text-maroon` if > 0).
         - Responsive layout: 2 distinct columns with 1px vertical divider on desktop (`md+`), collapsing seamlessly to a stacked key-value list with 1px dividers on mobile.
      3. **Actions Row**: Full-width stacked outline buttons on mobile (44px min height) and horizontal row on desktop:
         - `Download PDF` (direct PDF download)
         - `WhatsApp reminder` (prefilled WhatsApp follow-up link in chosen bill language)
         - `Customer portal ↗` (direct link to the client's public statement portal)
      4. **In-Place HTMX "Record Payment" Section (rendered only when balance due > 0)**:
         - Fields: `amount` (prefilled with exact balance due), `mode` dropdown (Cash / UPI / Bank transfer / Cheque), `reference` (12-digit UTR for UPI, cheque number for Cheque), `note`.
         - Primary maroon button `[ Save payment ]` (`btn-desk-primary`, 44px touch target on mobile).
         - Submits via HTMX targeting `#bill-detail-pane` with `hx-swap="outerHTML"`. On successful submission: updates balance, updates status dot, clears the form (or shows "Paid in full" banner), records verified `PaymentSubmission`, appends to payment history, and shows a calm success notice without a full page reload.
         - When balance is 0 (`balance_amount <= 0`), the form is omitted and replaced by a calm confirmation: `● This invoice is fully paid. No balance due.`
      5. **Strict Validation & Bilingual Errors**:
         - `amount` must be > 0 and cannot exceed `balance_amount`: inline errors in English (`"Amount must be greater than zero."`, `"Amount cannot exceed balance due (₹X)."` ) and Hindi (`"राशि शून्य से अधिक होनी चाहिए।"`, `"राशि शेष बकाया (₹X) से अधिक नहीं हो सकती।"`).
         - When mode is `UPI`, reference is strictly validated for 12 numeric digits (`"12-digit UTR is required for UPI payment."`, `"UTR must be exactly 12 digits (numeric only)."` / Hindi equivalents).
      6. **Payment History List**:
         - Clean data table below the form showing Date, Mode, Reference / UTR, and Amount (`tabular-nums`) for all payments made against the bill.
    - **Automated Test Suite**: Added comprehensive test cases covering amount validation (zero, negative, exceeding balance), 12-digit UPI reference enforcement, bilingual errors, partial + full HTMX payment recording, and two-column detail rendering. All 25/25 automated unit tests passing (100% OK).
    - **Visual Verification**: Captured and inspected via Chrome DevTools Protocol at 360px and 1200px across both English and Hindi (`bbill_detail_360.png`, `bbill_detail_1200.png`, `bbill_detail_hi_360.png`, `bbill_detail_hi_1200.png`, `bbill_detail_paid_1200.png`). Verified `scrollWidth == innerWidth == 360px` with zero horizontal overflow.
* **Complete High-Fidelity UI Mockup Suite (Tailwind CSS + HTMX)**:
  - **Master Interactive Application Suite (`dashboard_mockup.html`)**: Features persistent top Prototype Hub bar, live client-side tab & URL hash router (`#dashboard`, `#new-bill`, `#search-bills`, `#upi-queue`, `#bank-settings`, `#customer-portal`, `#bill-detail`), POS live calculation, Fernet AES-256 interactive masked account toggle, and customer UTR verification simulation.
  - **7 Dedicated Standalone Mockup Artifacts**:
    1. `mockup_dashboard.html`: Operations Dashboard with quick actions, KPI cards, UPI alert banner, and recent bills.
    2. `mockup_new_bill.html`: 2-column POS advertisement invoice creation form with live receipt preview.
    3. `mockup_search_bills.html`: Bill search and filter interface with date range and status filters.
    4. `mockup_upi_submissions.html`: Customer UPI verification queue with 1-click ledger credit.
    5. `mockup_bank_settings.html`: Official newspaper bank and UPI configuration with encryption and live QR code preview.
    6. `mockup_customer_portal.html`: Public customer self-service statement portal with 0-fee UPI deep-link and UTR submission.
    7. `mockup_bbill_detail.html`: Individual invoice detail view with payment recording and bilingual WhatsApp reminder.
* **PDF Invoicing UI/UX Architecture & Full A4 Implementation Complete v3.0 (billing/templates/billing/bill_pdf.html)**:
  - Fully implemented according to the v3.0 master architecture in `pdf-ui-improvement-plan.md` artifact.
  - **Full A4 Canvas Coverage**: Eliminating the half-page slip look by locking `.invoice-container` to exact A4 printable height (`278mm`) with a 2px ink outer border and full-height flex column.
  - **Expandable Ledger Spine Engine**: Table uses `height: 100%` with `tbody tr.item-row` (`height: 1px`) to hug content, and `tbody tr.blank-filler-row` (`height: auto`) absorbing remaining vertical space. Column rules run seamlessly down to the totals bar, creating an authentic bound ledger book aesthetic.
  - **Dual Format Architecture (Computer Generated vs. Physical Seal & Sign)**:
    - **Format A (Default, `sign=0`)**: Modern Computer Generated Document — Displays official green verified badge, Digital Verification ID (`Ref: VG-YYYY-NNNN`), and statutory declaration ("This is a computer generated invoice and does not require a physical signature — Information Technology Act, 2000").
    - **Format B (Optional, `sign=1`)**: Traditional Seal & Sign — Broadsheet physical signatory clearance box with newspaper stamp zone and authorized signatory underline for government/B2B clients requiring physical ink/rubber stamps.
    - **Interactive Format Switcher**: On-screen print preview toolbar (`.no-print-toolbar`) provides 1-click instant toggling between `[ Computer Generated ]` and `[ Seal & Sign ]`.
    - **Staff Action Buttons**: Added dual download buttons on `bill_detail_pane.html` (`[ Download PDF ]` for Computer Generated, `[ Seal & Sign PDF ]` for physical seal version).
  - **Scaled Component Proportions**: Scaled up logo (54px), masthead typography (14-16pt), metadata cards (min-height 84px), dynamic UPI QR code (86px), and signatory clearance to command the full page with balance.
  - **Universal Handling**: Sparse bills ("too blank") use structured metadata fallbacks and the ruled ledger spine; dense bills contract the filler row gracefully without overflow.
  - **Strict Pure-Language Invoicing Engine (100% Full English & 100% Full Hindi)**:
    - **Zero Language Mixing**: Completely eliminated bilingual slashes, parenthetical English translations in Hindi mode, and Hindi words bleeding into English documents.
    - **100% Full English (`lang=en`)**: Pure English headers (`ADVERTISEMENT INVOICE`, `Invoice No:`), English client name isolation (`client_display_name`), English placement/edition, pure English currency words (*"Rupees Three Thousand Five Hundred Only"*), pure English stamp (`✔ PAID IN FULL — PAYMENT SETTLED`), and 5 English legal clauses.
    - **100% Full Hindi (`lang=hi`)**: Authentic broadsheet Devanagari rajbhasha (`विज्ञापन देयक`, `बिल क्रमांक:`), Hindi client name isolation, Devanagari placement/edition, pure Hindi currency words (*"तीन हज़ार पाँच सौ रुपये मात्र"*), Hindi stamp (`✔ पूर्ण भुगतान प्राप्त — खाता चुकता`), and ५ वैधानिक शर्तें.
    - **Multi-Tier Option Switchers**:
      - Persistent On-Screen PDF Toolbar: Instant 1-click toggles for `Language: [ English | हिंदी ]` and `Format: [ Computer Generated | Seal & Sign ]` ($2 \times 2$ clean output matrix).
      - Staff Bill Detail Screen: Side-by-side action buttons `[ 📄 English PDF ]`, `[ 📄 हिंदी PDF ]`, and `[ ✍️ मुहर प्रति ]`.
      - Customer Statement Portal: Contextual matching — viewing in English downloads pure English PDF, viewing in Hindi downloads pure Hindi PDF.
  - **Verification**: Vector A4 PDFs (`invoice_full_english.pdf`, `invoice_full_hindi.pdf`, `invoice_computer_generated.pdf`, `invoice_physical_sign.pdf`) verified strictly 1 page each with 0 spills. High-res visual previews verified covering full A4 canvas. Automated test suite passing 27/27 tests (100% OK).
  - **Comprehensive UI Scale, Typography & Button Redesign Plan (`ui-typography-and-button-scale-plan.md`)**:
    - **Root-Cause Diagnosis**:
      1. Aggressive 12px CSS floor (`style.css: line 107`) forcing `font-size: 12px !important` on `.text-xs` and small elements, blocking responsive font scaling.
      2. Pervasive inline `font-size: 11px` styles in table headers and sublines.
      3. Devanagari script legibility failure: Mukta font at 11-12px blurs vowel matras and conjuncts. Minimum readable Devanagari scale is 14px (secondary) and 15-16px (body).
      4. Low-contrast, stubby 38px buttons with thin borders (`#e7e2d9`) and 12px text looking like badges rather than clickable tools.
      5. Table action links rendered as raw 11px text links (`View • PDF • WhatsApp • Portal`).
      6. Login page navbar leak: staff navigation tabs rendered to unauthenticated visitors; duplicate logo; cramped 400px card.
    - **Target Token Standards**:
      - Base body: 16px (was 15px); Secondary: 14px (was 11-12px); Floor: strictly zero text below 13px.
      - Financial KPI amounts: 32-36px bold tabular numbers (was 22px).
      - Primary buttons: 46-48px height, 15px font, bold weight, rich maroon `#9f1d1d`.
      - Secondary buttons: 44px height, 14px font, crisp `#d6cfc4` border.
      - Table actions: structured 32px segmented button pills (`[ View ]`, `[ PDF ]`, `[ WhatsApp ]`, `[ Portal ]`).
      - Login card: 440px wide, 48px inputs/button, auth-gated masthead navigation.
    - **Plan Artifact Generated**: `ui-typography-and-button-scale-plan.md` created with multi-page specifications, before/after table, and verification roadmap.
* **UI Typography, Button Scaling & Strict Vector Icon Integration Complete**:
  - **Eliminated CSS Size Floor**: Removed `font-size: 12px !important;` from `billing/static/billing/css/style.css`, allowing true responsive scaling across screens.
  - **Legible Mukta & Devanagari Typography**: Base body set to 16px, labels and subtext set to 14px, zero text below 13px on desktop. Crisp readability for conjuncts and matras.
  - **Strict Vector Icon System (Zero Emojis)**: Removed all Unicode emojis across templates and replaced them with vector Bootstrap Icons (`<i class="bi bi-..."></i>`):
    - `bi-file-earmark-pdf` for PDF downloads
    - `bi-pen` for Seal & Sign version
    - `bi-whatsapp` for WhatsApp reminders
    - `bi-arrow-up-right` for Customer portal
    - `bi-plus-lg` for Create bill
    - `bi-eye` for View invoice
    - `bi-box-arrow-in-right` for Sign In
  - **Auth-Gated Masthead (`partials/_masthead.html`)**: Navigation tabs and user session display are strictly restricted to authenticated staff (`{% if variant == 'staff' and user.is_authenticated %}`). Unauthenticated visitors on `/accounts/login/` see only the clean brand logo and language switcher.
  - **Staff Sign In Card (`login.html`)**: Removed duplicate inner logo. Scaled card width to 440px with 36px/32px padding, 48px inputs (16px font), and a prominent 48px primary Sign In button.
  - **Financial KPI Strip (`partials/stats_strip.html`)**: Scaled metric amounts to 32px bold tabular numbers with 13px/14px uppercase labels and 13px subline context.
  - **Dashboard Controls (`dashboard.html`)**: Scaled desktop search bar to 42px height (14px font), `+ New bill` button to 42px height, and debtor actions to 32px `.btn-desk-sm` buttons with Bootstrap icons.
  - **Bills Table Actions (`partials/bills_table.html`)**: Replaced raw 11px text links with structured 32px `.btn-desk-sm` buttons (`View`, `PDF`, `WhatsApp`, `Portal`) with crisp `#d6cfc4` borders.
  - **Bill Detail Pane (`partials/bill_detail_pane.html`)**: Scaled action buttons to 44px min-height with crisp `#d6cfc4` borders, scaled balance due to 24px bold maroon, and scaled payment inputs to 42px min-height.
  - **Search & Forms (`bill_search.html`, `bill_form.html`, `payment_submissions_list.html`)**: Standardized all form controls, chips, and filter selects to 42px height and 14px/15px typography.
  - **Automated Test Suite Verified**: All 27 automated unit tests passed (100% OK). Dev server running cleanly on port 8080.

---

## 7. Android Termux Co-Hosting Configuration
* **Host Device:** Xiaomi Redmi Note 8 Pro (MIUI 12.5.10 / Android 11, arm64-v8a)
* **Static IP:** `192.168.1.50`, SSH Port: `8022`
* **Port Isolation:**
  - Site 1 (Filvora): Port `8000` (`~/Filvora`, log `~/filvora.log`)
  - Site 2 (Vishwaguru Billing): Port `8080` (`~/vishwaguru-billing`, log `~/vishwaguru-billing.log`, pid `~/vishwaguru-billing.pid`)
* **Process Isolation:** Strict port-specific control commands (`pkill -f "runserver 0.0.0.0:8080"` or `fuser -k 8080/tcp`) to guarantee Filvora on 8000 is never touched.
* **SQLite Concurrency on Android:** WAL mode (`PRAGMA journal_mode = WAL;`) and connection timeout (20s) auto-configured in `billing/apps.py` and `config/settings.py`.
* **Termux Operational Helpers (Global $PREFIX/bin):**
  - `status` / `update`: Filvora (Site 1, Port 8000).
  - `status2` (`$PREFIX/bin/status2`): Checks if Vishwaguru Billing is alive on port 8080, checks PID, tests HTTP response at `http://192.168.1.50:8080/`, and prints log or error output.
  - `update2` (`$PREFIX/bin/update2`): Safely stops port 8080 (`pkill -f "runserver 0.0.0.0:8080"` and `fuser -k 8080/tcp`), runs `git pull` in `~/vishwaguru-billing`, runs migrations, and starts the server in background on port 8080 logging to `~/vishwaguru-billing.log`.
* **Network & Host Isolation:** `ALLOWED_HOSTS = ['*']` configured by default in `config/settings.py` so any PC on home Wi-Fi (`192.168.1.50`, `filvora`) and all devices on Tailscale (`filvora`, `*.ts.net`, 100.x IPs) connect without `DisallowedHost` blocks.
* **Cloudflare Tunnel (Custom Domain):**
  - `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')` and `USE_X_FORWARDED_HOST = True` configured in `config/settings.py` so HTTPS over Cloudflare Tunnels does not trigger 403 CSRF verification failures.
  - Tunnel runs on Termux using `cloudflared tunnel run --token <TOKEN>` routing `https://billing.yourdomain.com` to `127.0.0.1:8080`.


