# PROJECT_CONTEXT.md — Newspaper Ad Billing System

## Purpose
Internal tool for Vishwaguru newspaper to generate advertisement bills (PDF), track payment status, and log every bill for later search — replacing manual billing.

## Tech Stack
- Backend: Django (Python)
- DB: Postgres or MySQL, self-hosted locally
- PDF: WeasyPrint (HTML/CSS → PDF, generated on-demand, never stored as files)
- Frontend: Django templates + vanilla JS (live total calculation), no SPA framework
- Auth: Django built-in auth, all staff equal permission (no roles in v1)

## Architecture Decisions
- **Hosting: local PC**, not any PaaS. Rejected PythonAnywhere (free apps auto-disable after 30 days inactivity, 500MB disk cap, no custom domain) and Oracle Cloud (history of Always-Free account suspensions).
- **Remote access: Cloudflare Tunnel** (`cloudflared`) — free, no port forwarding, no exposed router port, gives real HTTPS URL.
- **Reliability:** Django (Gunicorn) + `cloudflared` run as systemd services, auto-restart on crash/reboot.
- **PDFs are never stored as files** — always regenerated live from the `Bill` DB row on request. Keeps storage trivially small and avoids managing a media folder.
- **GitHub Pages is unrelated to this project** — stays reserved for the existing portfolio/epaper site only.

## Repository
- Remote: `https://github.com/omtiwari17/vishwaguru-billing`
- Root layout: Direct root repository (no enclosing `billing_app` subfolder)

## File Structure
```
vishwaguru-billing/          # Repo root (this directory)
├── manage.py
├── billing/                # Django app
│   ├── models.py           # Bill, PaymentInfo
│   ├── views.py            # BillCreateView, BillDetailView, BillPDFView, BillSearchView, BillPaymentUpdateView
│   ├── forms.py            # BillForm, BillPaymentUpdateForm
│   ├── utils.py            # Bill number generator, UPI QR code generator, amount in words
│   ├── templates/billing/  # bill_form.html, bill_detail.html, bill_search.html, bill_pdf.html
│   ├── static/billing/     # CSS, JS (live total calc), logo image
│   └── urls.py
├── config/                 # Project settings & root urls
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── deploy/                 # Production deployment templates
│   ├── vishwaguru-billing.service
│   ├── nginx.conf
│   └── backup.sh
├── requirements.txt
├── .gitignore
├── README.md
├── HLD.md
├── LLD.md
├── PROJECT_CONTEXT.md
└── REQUIREMENTS.md
```

## Data Model Summary
- **Bill**: bill_number (`VG-YYYY-NNNN`), client_name, client_phone, client_address, client_gstin, placement_type (Front Full, Inside Half, Chouthai, etc.), custom_size_text, ad_title, edition_date, edition_name, epaper_link, page_number, base_amount, discount_amount, total_amount, payment_status (`Unpaid`/`Paid`/`Partial`), amount_paid, payment_method (`Cash`/`UPI`/`Bank Transfer`/`Cheque`), payment_note, created_by, created_at
- **PaymentInfo** (single row, admin-edited): bank_name, account_number, ifsc_code, upi_id, account_holder_name, phone_number, office_address

## Completed Alignment & Design (via /grill-me)
1. Pricing & Placement: Standard presets (Front Page Full, Inside Half, Chouthai, etc.) + customizable rate and custom size option.
2. Tax & Discounts: No GST calculations (all amounts all-inclusive) + optional discount field.
3. Bill Numbering: `VG-YYYY-NNNN` (resets to 0001 each calendar year).
4. Client Information: Client Name, Phone Number (for WhatsApp follow-up), Address/City, and optional GSTIN/PAN.
5. Dynamic UPI QR: Rendered directly on the PDF bill (`upi://pay?pa=...`) for scan & pay.
6. WhatsApp Sharing: 1-click WhatsApp share link on the bill details page.
7. Verification: Epaper URL + Page number field.
8. Letterhead: Logo image asset in `billing/static/billing/img/logo.png`.
9. Dev vs Prod: Develop on Windows (SQLite/Postgres) -> Deploy on Ubuntu Linux PC (Postgres + Gunicorn + Nginx + Cloudflare Tunnel + systemd).

## Current Work
- Awaiting user instruction to start code implementation.

## Pending Tasks
1. Initialize Django project and `billing` app directly in this root directory.
2. Implement models (`Bill`, `PaymentInfo`), migrations, and auto-numbering utility (`VG-YYYY-NNNN`).
3. Implement WeasyPrint PDF generator with dynamic UPI QR code, number-to-words, and Vishwaguru letterhead.
4. Implement clean, responsive UI with live amount calculation and 1-click WhatsApp sharing.
5. Create production deployment configurations in `deploy/`.

## Important Implementation Details
- Amount is recalculated server-side on submit even though JS calculates it live client-side (never trust client math for the saved value).
- Payment receiving info (bank/UPI) lives in one shared `PaymentInfo` row, not duplicated per bill — update once, reflects on all future PDFs.
- No role-based permissions in v1 — all logged-in staff have equal access.
- Self-hosted local setup means no managed-DB safety net — manual/automated backup script is included.
