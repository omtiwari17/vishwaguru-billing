# Requirements — Newspaper Advertisement Billing System

## 1. Project Purpose
An internal tool for a newspaper (Vishwaguru) to generate advertisement bills for clients. Staff enter ad details (size, rate, client, edition, epaper link, payment info), the system calculates the amount, generates a PDF bill, and logs every bill so it can be searched later.

## 2. Functional Requirements

| ID | Requirement | Notes |
|---|---|---|
| ID | Requirement | Notes |
|---|---|---|
| FR1 | Staff can create a new bill by entering: client details (name, phone, address, optional GSTIN/PAN), ad placement preset / size, rate/amount, discount, edition/date printed, epaper link, and page number | Core data entry |
| FR2 | System auto-calculates total amount (base amount - discount) with live feedback | Live calculation in UI |
| FR3 | System generates a downloadable PDF bill on submit | Regenerated on demand, not stored as a file |
| FR4 | Every bill is logged permanently in the database with unique sequential number `VG-YYYY-NNNN` | Client, ad placement, amount, dates, epaper link, payment info |
| FR5 | Staff can search/filter past bills by client name, phone, bill number, or date range | Single search box + date filter |
| FR6 | Staff can re-download/re-view the PDF of any past bill | Regenerated live from DB record |
| FR7 | Multiple staff can log in and use the tool | Django built-in auth, equal permissions for all staff (no role tiers in v1) |
| FR8 | Epaper link & Page Number are stored per bill and clickable from log view and PDF | Epaper URL + page number (e.g. Page 1, Page 4) |
| FR9 | PDF includes the epaper link so the client can verify the ad went live | Visible/clickable URL in PDF |
| FR10 | PDF includes payment details — bank/UPI info, dynamic UPI QR code, and payment status | Dynamic UPI QR code generated on-demand; bank info pulled from shared `PaymentInfo` config |
| FR11 | Payment status and method are recorded per bill and editable | Unpaid / Paid / Partial, with amount paid, payment method, and notes |
| FR12 | UI is simple enough for non-technical staff | Minimal fields per screen, clear labels, dropdowns over free text |
| FR13 | 1-Click WhatsApp share from bill details screen | Generates WhatsApp Web / App share link with pre-filled bill summary & epaper link |

## 3. Non-Functional Requirements

| ID | Requirement | Decision driving it |
|---|---|---|
| NFR1 | Reachable remotely, not just on office WiFi | Local hosting + Cloudflare Tunnel |
| NFR2 | Zero hosting/DB cost | Local PC hosting, no PaaS fees |
| NFR3 | Usable by non-technical staff | Simple one-screen forms, dropdowns, live total calculation |
| NFR4 | Data durability — bill records must not be lost | Local Postgres with regular automated backups via backup script/cron |
| NFR5 | Fast PDF generation | Under ~3 seconds per bill via WeasyPrint |
| NFR6 | Simple, maintainable — avoid unnecessary complexity | Plain Django monolith, no microservices, no unnecessary third-party services |
| NFR7 | Service resilience on local hardware | systemd services for Django + Cloudflare Tunnel daemon, auto-restart on crash/reboot |
| NFR8 | Secure remote access without exposing the router | Cloudflare Tunnel (outbound-only connection, no open inbound port) |

## 4. Out of Scope (v1)
- Online payment gateway integration (Razorpay/Paytm) — payments are manually tracked (Cash/UPI/Bank/Cheque)
- Multi-newspaper / multi-tenant support
- Automated epaper-link fetching from the Blogger site (manual paste only)
- Native mobile app (browser-based, responsive design is sufficient)
- Role-based permissions / admin hierarchy beyond Django's basic staff login
- GST tax calculations (all ad charges are all-inclusive flat totals)

## 5. Resolved Decisions
1. **Pricing & Placement:** Standard presets (Front Page Full, Inside Half, Chouthai, etc.) with customizable rate/amount, plus Custom Size option.
2. **Bill numbering format:** `VG-YYYY-NNNN` (e.g. `VG-2026-0001`), resetting to 0001 each calendar year.
3. **Letterhead/logo:** Vishwaguru logo image placed in static assets and embedded in PDF header.
4. **Epaper link & verification:** Epaper URL + Page Number field (e.g., Page 1, Page 4) displayed together on the bill.
5. **Client Details:** Client Name, Phone Number (for WhatsApp follow-up), Address/City, and optional GSTIN/PAN.
6. **Payment & PDF features:** Dynamic UPI QR Code directly on the PDF + 1-Click WhatsApp share button in UI.
7. **Environment:** Development on Windows (SQLite/Postgres) -> Deployment on Ubuntu/Debian Linux PC (Postgres + Gunicorn + Nginx + Cloudflare Tunnel + systemd).
