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
* **Git configuration:** `.gitignore` configured for Django, `.env`, SQLite, virtual environments, and temporary folders (`tmp/`, `temp/`, `*.tmp`).
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
  - **Automated Test Suite Verified**: All 27 automated unit tests passed (100% OK).
* **Dashboard Unslop & Editorial Polish Pass Complete (`unslop` pass)**:
  - **KPI Metrics Strip (`partials/stats_strip.html`)**: Replaced uppercase tracked labels with clean broadsheet sentence-case (`Today's billed`, `This month`, `Collected`, `Balance due`). Removed all inline style overrides; defined `.dashboard-kpi-strip` and `.dashboard-kpi` on strict 4px grid (padding 16px/24px, min-height 104px/112px).
  - **Payment Status Distribution Bar (`dashboard.html`)**: Introduced a calm 6px segmented proportional collection health bar (`.status-bar`) showing Paid (green), Partial (amber), and Unpaid (maroon) percentages computed cleanly in `views.py`.
  - **Recent Bills Table (`partials/bills_table.html`)**: Converted table headers (`th`) from uppercase tracked styling to sentence case. Removed redundant inline styles; quieted the row actions into clean, non-competing buttons.
  - **Clean Copy & Strict 4px Grid**: Removed trailing ellipses from search placeholders (`Search bills` / `बिल खोजें`). Standardized desktop search to 260px $\times$ 40px and primary action to `+ New bill` (Hindi: `+ नया बिल`).
  - **Automated Test Suite Verified**: All 27 automated unit tests passed (100% OK).
* **UI Craft Elevation Pass with `better-ui` & `styleseed`**:
  - **Eliminated Destructive Font-Size & Border Overrides**: Removed blunt inline `!important` font and border overrides from `base.html` and cleaned `app-refresh.css` to restore natural typographic hierarchy and authentic broadsheet density.
  - **Concentric Geometry & Elevation (`better-ui`)**: Integrated `--shadow-border` (`0px 0px 0px 1px rgba(28, 25, 23, 0.08), 0px 1px 2px -1px rgba(28, 25, 23, 0.06), 0px 2px 4px 0px rgba(28, 25, 23, 0.04)`) across panels and cards with concentric 6px outer radius and 4px inner button radius.
  - **Active Press Feedback & Optical Alignment**: Added `0.96` active press scale over 150ms with `cubic-bezier(0, 0, 0.2, 1)` on all interactive buttons, chips, and table pills (`:not(:disabled):active`). Added 2px optical alignment on icon side for leading/trailing icons. Guarded hovers under `@media (hover: hover)` and motion under `@media (prefers-reduced-motion: reduce)`.
  - **Screen 1: Staff Sign In (`login.html`)**: Auth-gated navbar tabs in `_masthead.html` to present a distraction-free gateway. Centered 420px broadsheet card with official newspaper logo, Noto Serif Devanagari heading, 44px inputs with calm maroon focus rings (zero red borders when valid), 44px primary button, and internal desk security notice.
  - **Screen 2: Dashboard (`dashboard.html`, `stats_strip.html`, `bills_table.html`)**: Clean masthead tabs, 4-cell broadsheet KPI strip with hairline dividers and tabular numbers, recent bills table with sentence-case headers and `.desk-action-pill` buttons (`View`, `PDF`, `WhatsApp`, `Portal`), proportional collection bar, and overdue accounts panel.
  - **Screen 3: Bill Detail (`bill_detail.html`, `bill_detail_pane.html`)**: Breadcrumb with speedometer icon, 28px Noto Serif Devanagari invoice heading with status pill, 2-column broadsheet ledger (Client & Publication on left, Financial summary box on right), authoritative action toolbar with strictly vector Bootstrap icons (ZERO Unicode emojis), refined settlement banner, and tabular payment history.
  - **Automated Test Suite Verified**: All 27 automated unit tests passed (100% OK).
* **Full-Site HTMX, Modern CSS & Vanilla JS Architecture Integration**:
  - **Live HTMX Segmented Status Filters (`dashboard.html` & `views.py`)**: Added an interactive segmented tab track (`All`, `Unpaid`, `Partial`, `Paid`) with live `hx-get` filtering and out-of-band updates, avoiding full-page reloads.
  - **Modern CSS & Specular Craft (`style.css`)**:
    - Segmented track with nested radius geometry ($R_{track} = 6	ext{px}$, $p = 3	ext{px}$, $R_{tab} = 4	ext{px}$).
    - Active status tab specular highlight (`box-shadow: 0 1px 2px rgba(0,0,0,0.05), inset 0 1px 0 rgba(255,255,255,0.9)`).
    - 2.5px indeterminate shimmer loading bar (`.desk-shimmer-bar`) on in-flight HTMX queries.
    - Accessible `.table-wrapper` with keyboard scrollability (`tabindex="0"`, `role="region"`), sticky `thead th`, and CSS `content-visibility: auto` rendering containment for high INP responsiveness.
  - **Modern Vanilla JS Engine (`billing/static/billing/js/desk.js`)**:
    - **Global Keyboard Shortcuts**: Press `/` or `⌘K`/`Ctrl+K` to focus search with select-all; `Esc` to clear and blur; `N` to navigate directly to new bill creation.
    - **Modern Clipboard Helper**: Supports `[data-copy]` and `[data-copy-value]` attributes across settings and statement portals with instant visual checkmark confirmation.
    - **HTMX Progress Handlers**: Automatically triggers the shimmer loading bar during live search typing and tab swaps.
  - **Automated Test Suite Verified**: All 27 automated unit tests passed (100% OK).
* **Widescreen Desktop Layout & Broadsheet Typography Scale Upgrade**:
  - **Eliminated Excessive Left/Right Margins**: Replaced the narrow `1180px` / `1240px` container limits in `style.css` and `app-refresh.css` with a broad responsive container (`max-width: 1680px` up to `1800px` on widescreen 1536px+, with fluid 20px–44px inner padding). Fully resolves the dead 350px+ gutters on 1080p and widescreen monitors.
  - **Elevated Typographic Scale Across Whole Site**:
    - Root font scale: `16px` on mobile, `17px` on desktop (1024px+), `18px` on wide screens (1440px+).
    - KPI cards: labels 14px–15px, numbers 36px bold tabular-nums, subtext 14px, cell padding 22px–28px.
    - Data tables (`bills_table.html`, `bill_search.html`): headers 14px font-semibold (padding 14px 18px), cell primary text 16px, secondary muted text 14px, amounts 17px–18px bold tabular numbers (padding 15px 18px).
    - Controls & Actions: search bar 320px width x 44px height, primary buttons 44px–46px height, micro action pills (`View`, `PDF`, `WhatsApp`, `Portal`) 36px height with 14px typography.
    - Masthead & Nav: logo 40px–44px, nav tabs 46px height with 16px typography, language toggle 14px.
  - **Removed Hardcoded Inline Constraints**: Cleaned restrictive inline `font-size: 13px;` from `bills_table.html` and `bill_search.html`, and removed the `max-width: 920px;` double wrapper from `bill_detail.html`.
  - **Cache Busting**: Bumped asset cache-busting query strings to `?v=20261105-wide-6` across `base.html` and `customer_portal.html`.
  - **Automated Test Suite Verified**: All 27 automated unit tests passed (100% OK). Dev server running cleanly on port 8000/8080.
* **Widescreen Fluid Layout, Form Anti-Clashing & Typography Upgrade**:
  - **Resolved TemplateSyntaxError in `bill_form.html`**: Loaded `billing_tags` along with `static` on line 2, resolving the 500 error preventing the new form from rendering.
  - **Fluid Broadsheet Layout (Zero Wasted Margins)**: Upgraded `.office-container` across `style.css` and `app-refresh.css` to `max-width: 100%` / up to `1920px` with fluid responsive padding (`20px` mobile, `32px` tablet, `40px` desktop, `48px` wide screens), eliminating large dead gutters on 1080p monitors.
  - **Anti-Clashing Step Body Architecture**: Every `.step-card` now encloses form inputs inside a `.step-body` with `28px` internal padding and `24px` vertical gap (`18px` on mobile), ensuring zero labels or inputs touch or clash with card borders.
  - **Elevated Form Controls & Custom SVG Chevrons**: Standardized `.form-control` and `.form-select` to `50px` min-height, `16px` font size, `12px 18px` inner padding, and `6px` radius with custom inline SVG chevrons (`padding-right: 44px`) so text never collides with native OS arrows.
  - **Structured Placement Selection**: Presets chips (`.chip-btn`, `44px` height, `15px` font) and placement dropdown now feature a clear helper label (`Or select standard placement from dropdown:`), eliminating confusion and tight stacking.
  - **Expanded Sticky POS Receipt**: Increased sidebar width to `400px` with `24px` padding, `16px` line items, `32px` bold tabular-nums net total, and full-width `52px` `Generate Bill & Print` button.
  - **Recently Generated Invoices Panel**: Converted the bottom table in `bill_form.html` to a clean `.desk-panel` using `status_dot.html`, `16px` text, and Indian currency formatting.
  - **Automated Test Suite Verified**: All 27 automated unit tests passed (100% OK).
* **Payment Info Settings Restyling (`payment_info_settings.html`)**:
  - **Eliminated Wasted Margins**: Integrated with widescreen `.office-container` (fluid width up to `1920px`) and `.settings-workspace` (`1fr 380px` on desktop, `1fr` on tablet/mobile).
  - **Anti-Clashing Step Body Architecture**: Wrapped both Section 1 (Payment Accounts) and Section 2 (Newspaper Masthead) inside `.step-body` with `28px` internal padding and `24px` vertical gap, ensuring zero inputs touch or collide with card borders.
  - **Elevated Inputs & Typography**: All form fields standardized to `50px` height, `16px` font size, `12px 18px` inner padding, and `6px` radius.
  - **Highlighted UPI Card**: Enlarged and padded green panel (`background: #f0fdf4; border: 1px solid #bbf7d0; padding: 22px 24px;`) with prominent `16px` label and `13.5px` explanation.
  - **Right Sidebar Polish**: Active credentials card with `15px–16px` bold values, masked account toggle, 1-click UPI copy button, centered live QR test card (`160x160px`), and Fernet encryption compliance note.
  - **Cache Busting**: Bumped asset version to `?v=20261105-wide-7`.
  - **Automated Test Suite Verified**: All 27 automated unit tests passed (100% OK).
* **Bill Detail Screen Craft Elevation with `better-ui` & `styleseed` (`bill_detail.html`, `bill_detail_pane.html`)**:
  - **Eliminated Container Bottleneck**: Removed hardcoded `max-width: 1360px` in `bill_detail.html`, enabling full alignment with the widescreen broadsheet layout up to `1920px`.
  - **Elevated Typographic Scale**: Invoice title scaled to `32px–36px` bold tabular Noto Serif Devanagari, Client name to `24px` bold, financial numbers to `24px–30px` bold tabular nums, and body labels to `15px–16px`.
  - **Concentric Geometry & Layered Depth (`better-ui`)**: Outer ledger cards use `6px` radius with `--shadow-border`, enclosing the financial summary box with concentric `6px` radius and `24px` inner padding.
  - **Authoritative Action Toolbar**: Upgraded action buttons (`English PDF`, `Hindi PDF`, `Seal & Sign`, `WhatsApp Reminder`, `Customer Portal`) to `min-height: 44px`, `15px` typography, `10px 20px` padding, optical alignment (2px less padding on icon side), and `0.96` active press scale.
  - **Refined Payment History Table**: Converted table to `.data-table` with `14px` sentence-case headers, `16px` rows, `17px` bold tabular amounts, and generous `16px 18px` cell padding.
  - **Cache Busting**: Bumped asset query version to `?v=20261105-wide-9`.
  - **Automated Test Suite Verified**: All 27 automated unit tests passed (100% OK).
* **Bill Detail Overlapping Boxes & Lines Elimination Pass**:
  - **Root Cause Eliminated**: Removed colliding inner horizontal divider lines that were cutting across text descenders and causing visual box overlap in the financial summary and publication sections.
  - **Strict 24px Rhythmic Separation**: Enforced explicit `margin-bottom: 1.5rem;` (24px) via inline styles on all top-level sections (Primary Ledger -> Actions Toolbar -> Settled Banner -> Payment History), preventing cards from sticking or colliding.
  - **Clean Isolated Financial Card**: The financial summary is now housed in a single clean tinted box (`background-color: var(--paper); border: 1px solid var(--rule); border-radius: 6px; padding: 22px 24px;`) with a natural vertical `gap: 12px;` and only two functional dividers (dashed line before totals, solid line before balance due).
  - **Spacious Payment History Table**: Added `background-color: var(--paper);` and `padding: 12px 18px;` to table headers and `padding: 14px 18px;` to table rows with clean separation below the section title.
  - **Automated Test Suite Verified**: All 27 automated unit tests passed (100% OK).
* **Headless Browser Automated Layout Verification & Comprehensive Polish Pass**:
  - **Automated Headless CDP Inspection Suite**: Developed and executed `scratch/run_browser_inspector.py` using Chrome DevTools Protocol to inspect live pages (`/bills/`, `/bills/new/`, `/bills/settings/payment-info/`, `/bills/3/`, `/bills/search/`) for horizontal overflow, vertical collisions, overlapping boxes, and small font violations.
  - **Zero Overlap & Zero Layout Clashing Verified**: Live automated evaluation confirmed 0 horizontal overflows and 0 vertical collisions across all top-level desk panels, step cards, and grids.
  - **Bill Detail (`/bills/3/`) Refinements**:
    - Replaced the wide-split `display: flex; justify-content: space-between;` in Publication Details with a structured key-value CSS grid (`grid-template-columns: 140px 1fr; gap: 8px 16px;`), eliminating the awkward 500px void between labels and values.
    - Removed the redundant stray green dot on the far right of the Settled Banner (`This invoice is fully paid. No balance due.`).
    - Fixed the WhatsApp action button copy to dynamically say "Share on WhatsApp" / "व्हाट्सऐप रसीद" when the balance is ₹0, and "WhatsApp reminder" / "व्हाट्सऐप तगादा" only when balance is outstanding.
    - Enforced explicit 24px vertical separation above and below all sections, preventing any collision between the banner and payment history.
  - **Create Bill (`/bills/new/`) & Search (`/bills/search/`) Metric Strips**:
    - Replaced the bulky, outdated `.dashboard-stats-grid` and colored `.stat-chip` elements with the unified `.dashboard-kpi-strip` with 1px vertical borders, matching the dashboard broadsheet aesthetic.
    - Updated amount formatting in tables to use the `indian_currency` filter (e.g. `₹3,500` instead of `₹3500.00`).
  - **Cache Busting**: Bumped asset query strings to `?v=20261105-v11-desk` in `base.html` and `customer_portal.html` to guarantee immediate browser invalidation of cached stylesheets and scripts.
  - **Automated Test Suite Verified**: All 27 automated unit tests passed (100% OK).
* **Visual Craft & UI Polish Pass (Human Design Review)**:
  - **Eliminated Artificial Side Margins ("Too Much Border in Left and Right")**: Removed the `1840px`/`1920px` max-width container chokehold across `.office-container` in `style.css` and `app-refresh.css`, allowing the desk UI to fluidly use the widescreen width with comfortable `36px` padding.
  - **Bill Detail Architectural Overhaul (`/bills/3/`)**:
    - Eliminated nested boxes: merged client metadata and financial settlement into a single broadsheet card with a clean 1px vertical rule dividing the two columns (`1fr 380px`).
    - Enclosed action buttons in a dedicated clerk toolbar (`padding: 14px 20px`, `44px` height).
    - Fixed WhatsApp copy to say "Share on WhatsApp" on settled invoices, avoiding embarrassing reminder notices to paid clients.
    - Added generous 28px vertical separation around the settled banner and payment history table, eliminating visual collisions.
  - **Create Bill Form Polish (`/bills/new/`)**:
    - Added a primary `[ Generate Bill & Print ]` button directly at the bottom of Step 3 so staff can submit without hunting for the right sidebar.
    - Unified the top 4-metric strip with the clean broadsheet `.dashboard-kpi-strip`.
    - Increased form field vertical rhythm (`margin-bottom: 22px; label-gap: 8px; input-height: 48px; font-size: 16px`).
  - **Cache Invalidation**: Bumped static query string to `?v=20261105-v12-fluid` across `base.html` and `customer_portal.html`.
  - **Automated Test Suite Verified**: All 28 automated unit tests passed (100% OK).
* **Fault-Tolerant Cryptography & Termux Resilience**:
  - **Graceful Cryptography Fallback (illing/crypto.py)**: rom cryptography.fernet import Fernet, InvalidToken is now wrapped in a safe 	ry...except ImportError. If cryptography is not yet installed on low-resource hosts (e.g. Android Termux without rust compiler), Django will never crash with ModuleNotFoundError.
  - **Zero-Dependency Standard-Library Stream Cipher**: Transparently falls back to an authenticated HMAC-SHA256 stream cipher (enc:std:...) using Python's built-in hashlib, hmac, and os.urandom. Sensitive data remains encrypted at rest even without external C/Rust dependencies.
  - **Termux Pre-compiled Binary**: Documented pkg install -y python-cryptography for Android Termux hosts.
  - **Automated Test Suite Verified**: All 28 automated unit tests passed (100% OK).

---

* **Comprehensive Mobile Responsive Layout Overhaul & Zero-Collision Verification**:
  - **Bill Detail (`/bills/<id>/` & `bill_detail_pane.html`)**:
    - Replaced the rigid inline grid `grid-template-columns: 1fr 380px; gap: 3rem;` with `.bill-detail-grid` (1 column on `< 1024px`, 2-column `1fr 380px` on desktop).
    - Client Details and Billing & Settlement stack cleanly on mobile with a distinct 1px rule divider (`border-top: 1px solid var(--rule); padding-top: 1.5rem; margin-top: 1.5rem;`).
    - Fixed publication details into responsive `.meta-row` (`grid-template-columns: 1fr; gap: 3px;` on mobile, `130px 1fr` on `sm+`), preventing words from breaking into vertical single-character columns.
    - Upgraded action toolbar into `.bill-actions-bar` (2-column touch-friendly grid on mobile, inline flex bar on desktop) with $\ge 44	ext{px}$ touch targets.
  - **Bank & UPI Settings (`/bills/settings/payment-info/`)**:
    - Replaced hardcoded inline style on `.settings-workspace` with responsive CSS (`grid-template-columns: 1fr;` on mobile, `1fr 380px;` on `lg+`), restoring the form to full width and stacking the credentials preview below it on small viewports.
    - Updated top panel padding to fluid scaling `clamp(16px, 3vw, 26px)`.
  - **Dashboard (`/bills/` & `dashboard.html`)**:
    - Reordered mobile layout: Mobile Header (`Recent bills` title, count, full-width search bar, side-by-side `+ New bill` & `View all` buttons) placed directly *above* the Segmented Status Filter Tabs Bar.
    - Scoped `.bills-desk-panel` to unboxed/transparent on mobile and boxed on desktop (`@media (min-width: 768px)`), eliminating boxed border collisions.
    - Filter tabs set to smooth horizontal touch-scrolling (`overflow-x: auto; white-space: nowrap; -webkit-overflow-scrolling: touch;`), eliminating wrapping and text overlaps.
  - **Mobile Actions & Three-Dot Dropdown Overhaul (`partials/bills_table.html` & `desk.js`)**:
    - **Mistakes Identified & Eliminated**:
      1. Replaced literal ASCII `&hellip;` character with vector Bootstrap Icon `<i class="bi bi-three-dots-vertical"></i>` inside a clean `.btn-desk-sm` trigger button.
      2. Removed fragile full-card stretched link (`a.absolute.inset-0`) that caused accidental navigation when tapping near the three-dot button or menu.
      3. Fixed dropdown menu positioning: `.desk-menu-box` anchored to `right: 0; top: calc(100% + 4px);` with `0 4px 16px rgba(0, 0, 0, 0.1)` elevation, 1px `#e7e2d9` border, and smooth fade-in animation.
      4. Restored missing WhatsApp action: Menu now includes all 4 options (View Invoice, Download PDF, WhatsApp Receipt / Reminder, Client Statement Portal).
      5. Added auto-dismiss in `desk.js`: Dropdowns automatically close on click-outside, Escape key, or when opening another menu.
    - **Direct 1-Click Action Buttons on Mobile Cards**:
      - Brought "the other buttons" (`[ View ]`, `[ PDF ]`, `[ WhatsApp Remind / Receipt ]`, `[ Portal ]`) directly onto the bottom of every mobile bill card in a dedicated action row.
      - Staff no longer need to open the three-dot menu for common tasks, giving instant 1-tap access with $\ge 40	ext{px}$ touch targets.
  - **Staff Login Screen Overhaul (`login.html`)**:
    - **Eliminated Logo Duplication**: Removed the redundant secondary logo from inside the login card, letting the official masthead logo in the top navbar stand out cleanly.
    - **Security Medallion & Dignified Typography**: Added a central maroon security seal (`bi bi-shield-lock-fill`) and switched title and labels to clean Mukta typography with balanced hierarchy.
    - **Interactive Password Visibility Toggle**: Integrated a 1-click password show/hide eye toggle button (`bi bi-eye` / `bi bi-eye-slash`) directly in the password input.
    - **Mobile Touch Comfort**: Applied fluid padding `clamp(22px, 5vw, 36px)` and 48px input/button heights, ensuring comfortable typing and zero horizontal overflow on small mobile screens.
    - **Verified Authentication**: End-to-end login flow verified via CDP script; automated unit test suite passing 28/28 (100% OK).
  - **Automated Verification**:
    - CDP Headless Chrome mobile inspection verified across `390x844` and `427x952` with zero horizontal overflow (`scrollWidth == innerWidth`).
    - Desktop inspection verified at `1280x900` with 2-column layouts and responsive metrics intact.
    - Automated test suite: 28/28 tests passing (100% OK).

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


