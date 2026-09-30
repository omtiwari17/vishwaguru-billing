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
* **Active branch:** `feature/customer-statement-portal` (created from `main`).
* **Code status: Customer Self-Service Statement Portal & Zero-Fee UPI Payment Complete.**
  - Django project (`config`) and billing app (`billing`) active on port 8080.
  - Models (`Bill`, `PaymentInfo`, `Client`, `PaymentSubmission`) fully migrated.
  - All 14 automated unit tests passed (100% OK).
  - **Customer Self-Service Statement Portal (`/statement/<uuid:token>/` & `/c/<uuid:token>/`):**
    - Secure, unguessable UUID token per client (`Client.access_token`) — zero login required for clients.
    - Mobile-first, bilingual statement view (`[ English | हिन्दी ]`).
    - 4 Financial Ledger Summary Cards: Total Ads Published, Total Billed, Total Paid, and Outstanding Balance Due (कुल शेष बकाया).
    - Distinct ledger sections: Unpaid/Pending Advertisements vs. Cleared/Paid in Full History.
    - Public bill PDF download directly from statement portal without staff credentials (`/statement/<token>/bill/<id>/pdf/`).
    - 1-click verification of online published ads via e-paper link.
  - **Zero-Fee Native UPI Payment Integration:**
    - Deep-linking (`upi://pay?pa=...&pn=...&am=...&tn=...&cu=INR`) opens user's installed UPI app (Google Pay, PhonePe, Paytm, BHIM, Cred) with prefilled amount and payee.
    - Zero intermediary transaction fees (100% direct bank-to-bank settlement).
    - Dynamic UPI QR Code for desktop/tablet scanning.
    - Bank details (Account Number, IFSC, UPI ID) with 1-click copy buttons.
    - Individual bill UPI payment or total balance settlement.
  - **Customer UTR Submission & Staff Verification Flow:**
    - Customers submit their 12-digit UTR or UPI reference ID directly on their statement page.
    - Creates `PaymentSubmission` records in database.
    - Shows real-time pending verification alert banners on the customer's portal.
    - Staff dashboard (`/bills/submissions/`) and Bill Detail screen (`/bills/<id>/`) feature 1-click **[ Verify & Confirm Paid ]** action buttons that instantly credit the bill and update payment notes with the UTR.
  - **Staff Sharing & Management:**
    - 1-Click WhatsApp statement share button on `bill_detail.html` pre-formatted with balance due and statement URL.
    - Direct Customer Portal preview link on `bill_detail.html` and `bill_search.html`.
    - Navigation link to UPI Verifications in top navbar.

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
* Feature implemented and verified on branch `feature/customer-statement-portal`.
* Automated test suite: 14/14 tests passing.
* User explicitly instructed to commit and push on this branch.


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


