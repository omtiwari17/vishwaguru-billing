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
* **Purpose:** Internal ad billing, tracking, and bilingual PDF generation system for **Vishwaguru Newspaper**. Replaces manual billing with instant PDF generation, payment tracking, and a searchable bill database.
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
   - Dynamic UPI QR Code generated on-demand via `qrcode` package (`upi://pay?pa={upi_id}&pn=Vishwaguru&am={total_amount}&tn={bill_number}`).
   - Amount in words auto-rendered in Hindi and/or English.

7. **UI / UX Features:**
   - Single-screen bill creation with live total calculation (vanilla JS).
   - 1-Click "Share on WhatsApp" button on bill details screen (`https://wa.me/{phone}?text=...`) formatted in the chosen bill language.
   - Search & filter past bills by client name, phone, bill number, or date range.

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
    - `submission_row_verified.html`: Row-level verify/reject feedback with OOB navbar badge swap.
  - **HTMX Enhancements:**
    - Live search in bills table via HTMX debounce without full page reload.
    - Row-level verify/reject actions for customer UPI submissions.
    - Out-of-band updates (`hx-swap-oob="true"`) for the navbar pending verification count badge.
  - **Phase 1 Complete:** `base.html` and `dashboard.html` fully restyled and verified against test suite (20/20 OK) and visual rendering.
  - **Phase 2 Polish Complete:**
    - Dual Layout in `partials/bills_table.html`: dense tabular view on `md+` (`hidden md:block`) and stacked cards on small screens (`block md:hidden`).
    - Stacked card layout: Line 1 = Invoice no + date + status dot; Line 2 = Client name + phone; Line 3 = Placement & edition; Line 4 = Total amount + Balance due.
    - Actions on mobile: Visible primary green WhatsApp button ($\ge 44\text{px}$ touch target) + clerk `...` `<details>` menu containing View invoice, Download PDF, and Statement portal links (each $\ge 44\text{px}$).
    - Stats Strip: $2\times 2$ grid with 1px dividers on mobile, 4-metric horizontal divider strip on desktop, increased cell padding, and 24px vertical separation before the bills panel.
    - Indian Currency Filter: `indian_currency` filter in `billing/templatetags/billing_tags.py` (`₹1,84,200` without `.00` unless paise exist).
    - Authentic Pluralization: `bill_noun` & `bill_count_label` filters for English ("1 bill" vs. "2 bills") and Hindi ("1 बिल" vs. "2 बिल", "1 ग्राहक का भुगतान" vs. "N ग्राहकों के भुगतान").
    - Unified Newspaper Identity: "दैनिक विश्वगुरु की झलक" in Hindi and "Vishwaguru Newspaper" in English across masthead, titles, and footer.
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
    - **Bilingual Page Translations**: Custom `format_page` filter accurately renders `"Page X"` $\to$ `"पृष्ठ X"` across both desktop and mobile views. Verified masthead identity `"दैनिक विश्वगुरु की झलक"` and Hindi subtitles.
    - **Verification**: Verified across 360px, 390px, 800px, and 1200px viewports in both English and Hindi. Automated test suite: 20/20 tests passing (100% OK).
* **Complete High-Fidelity UI Mockup Suite (Tailwind CSS + HTMX)**:
  - **Master Interactive Application Suite (`dashboard_mockup.html`)**: Features persistent top Prototype Hub bar, live client-side tab & URL hash router (`#dashboard`, `#new-bill`, `#search-bills`, `#upi-queue`, `#bank-settings`, `#customer-portal`, `#bill-detail`), POS live calculation, Fernet AES-256 interactive masked account toggle, and customer UTR verification simulation.
  - **7 Dedicated Standalone Mockup Artifacts**:
    1. `mockup_dashboard.html`: Operations Dashboard with quick actions, KPI cards, UPI alert banner, and recent bills.
    2. `mockup_new_bill.html`: 2-column POS advertisement invoice creation form with live receipt preview.
    3. `mockup_search_bills.html`: Bill search and filter interface with date range and status filters.
    4. `mockup_upi_submissions.html`: Customer UPI verification queue with 1-click ledger credit.
    5. `mockup_bank_settings.html`: Official newspaper bank and UPI configuration with encryption and live QR code preview.
    6. `mockup_customer_portal.html`: Public customer self-service statement portal with 0-fee UPI deep-link and UTR submission.
    7. `mockup_bill_detail.html`: Individual invoice detail view with payment recording and bilingual WhatsApp reminder.

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


