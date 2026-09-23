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
* **Active branch:** `main` tracking `origin/main`.
* **Code status: Client Memory, Old Pending Due in Bill, and Lowered PDF Layout Complete.**
  - Django project (`config`) and billing app (`billing`) active on port 8080.
  - Models (`Bill`, `PaymentInfo`, `Client`) migrated.
  - All 12 automated unit tests passed (100% OK).
  - High-speed **2-Column POS Billing Workstation**:
    - **Client Autocomplete & Memory:** Suggests past clients dynamically as staff types; auto-fills phone, address, and GSTIN/PAN.
    - **Old Pending (Previous Due / पुराना बकाया):** Automatically detects unpaid balances for returning clients; 1-click **[Add to Bill]** shortcut updates total payable amount `(Base - Discount) + Previous Due`.
    - **Step-by-step inputs** on the left with progressive disclosure.
    - **1-Click Preset Chips** for common ad placements (`Front Full`, `Front Half`, `Front Quarter`, `Inside Half`, `Ear Panel`, `Custom Size`).
    - **Smart Defaults:** `edition_date` defaults to today (`timezone.localdate()`) with `[ Today ] [ Tomorrow ]` shortcuts; `edition_name` defaults to Indore; `payment_status` defaults to Paid.
    - **1-Click Status Pills:** `[ Paid in Full ]` (auto-fills total amount), `[ Unpaid ]`, and `[ Partial ]`.
    - **1-Click Method Pills:** `[ Cash ]`, `[ UPI / QR ]`, `[ Cheque ]`, `[ NEFT ]`.
    - **Sticky Live POS Invoice Receipt:** Real-time synchronization of client name, placement, edition date, previous due, calculations, balance due, and prominent "Generate Bill & Print" action button.
    - **Lowered PDF Layout:** A4 invoice positions totals and bank/QR details in the lower section of the page with balanced spacing, eliminating empty void at the bottom.
    - **Live Dashboard Stats Bar:** Displays Today's Bills, Total Billed, Total Collected, and Pending Due.
    - **Recent Bills Quick Drawer:** Instant reprint, PDF download, and WhatsApp sharing without leaving the creation screen.
    - Modern CSS design system with responsive mobile breakpoints and 48px+ touch targets.

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

## 6. Pending Actions / Next Steps
* Awaiting user testing on:
  - Client autocomplete suggestions while typing client name.
  - 1-Click addition of old pending due into bills.
  - Lowered amount and bank details layout on A4 PDF invoices.
* When instructed by the user, run `git commit` to commit the codebase (NO push!).


