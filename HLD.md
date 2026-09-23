# High-Level Design (HLD) — Newspaper Advertisement Billing System

## 1. Architecture Style
A simple **monolithic Django application**, server-rendered HTML templates (no separate frontend framework). One deployable unit, self-hosted. This matches the project's "simple over clever" principle and the existing Django/Python skillset.

## 2. Hosting Decision (final)

| Concern | Decision | Why |
|---|---|---|
| App hosting | Local PC (old machine repurposed as a server) | Free, unlimited disk/CPU, no PaaS caps, no account-expiry risk |
| Database | Local Postgres or MySQL on the same PC | Free, no size limits tied to a hosting provider's quota |
| Remote access | Cloudflare Tunnel (`cloudflared`) | Free, secure outbound-only tunnel — no port forwarding, no exposed router port, gives a real HTTPS URL reachable from anywhere |
| Reliability | systemd services for Django (Gunicorn) + `cloudflared`, with auto-restart on crash/reboot | Local hosting requires the app to survive PC reboots without manual intervention |
| GitHub Pages | Not used for this tool | Static-only; remains reserved solely for the existing portfolio/epaper site |
| PythonAnywhere (rejected) | Considered, rejected | Free web apps auto-disable after 30 days of inactivity; 500MB disk ceiling; no custom domain on free tier |
| Oracle Cloud Free Tier (rejected) | Considered, rejected | History of "Always Free" accounts being suspended/flagged even when legitimately used |

**Accepted trade-off:** if the local PC is off, crashed, or loses power/internet, the tool is unreachable. No free hosting option removes this entirely for self-hosted setups; it's mitigated (not eliminated) by systemd auto-restart and keeping the PC running during business hours.

## 3. System Components

```
┌───────────────────────────────┐
│   Staff (office or remote)    │
└───────────────┬────────────────┘
                │ HTTPS via Cloudflare Tunnel
┌───────────────▼──────────────────────────────┐
│              Old PC (local server)             │
│                                                 │
│  ┌────────────┐   ┌─────────────────────────┐ │
│  │ Django app │   │ Postgres/MySQL (local)   │ │
│  │ (Gunicorn) │──▶│  - Bill records           │ │
│  │            │   │  - PaymentInfo config     │ │
│  │            │   │  - Users (staff logins)   │ │
│  └─────┬──────┘   └─────────────────────────┘ │
│        │                                       │
│  ┌─────▼───────────────┐                       │
│  │ PDF generator        │  (WeasyPrint,         │
│  │ (on-demand, no       │   renders live from   │
│  │  stored PDF files)   │   Bill row data)      │
│  └──────────────────────┘                       │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │  cloudflared (Cloudflare Tunnel daemon)     │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  Both Django and cloudflared run as systemd     │
│  services — auto-start on boot, auto-restart    │
│  on crash                                       │
└─────────────────────────────────────────────────┘
```

## 4. Data Flow

1. Staff logs in (Django auth) → opens "New Bill" form
2. Staff enters client details (name, phone, address, optional GSTIN), selects ad placement preset (Front Full, Inside Half, Chouthai, etc. or Custom), rate, optional discount, edition, date, epaper link, page number, and payment status/method
3. Frontend JS live-calculates the net total amount (`base_amount - discount`) as inputs change
4. On submit: Django validates → calculates final amount server-side → assigns sequential bill number `VG-YYYY-NNNN` → saves a `Bill` row to the DB
5. Django renders the PDF immediately from the saved `Bill` row + shared `PaymentInfo` (including dynamic UPI QR code and number-to-words), using WeasyPrint → returns it for download (not saved to disk)
6. Staff can open "Search Bills" → filter by client/phone/bill number/date range → view bill details, copy/click 1-click WhatsApp share link, or re-download PDF regenerated on the fly

## 5. Why On-Demand PDF Generation (No File Storage)

- A `Bill` DB row is a few hundred bytes; a stored PDF file is 50–150KB
- Since bill data never changes after creation, the PDF is always identical whether stored or regenerated — no reason to store it
- At realistic volume (tens of bills/day for years), the DB stays a few tens of MB; local disk space is a non-issue either way, but this keeps the design lean and avoids managing a growing media folder

## 6. Security Notes
- All views require login (`@login_required`) — no public/anonymous access to bill data
- Cloudflare Tunnel exposes only what's explicitly tunneled — no other ports on the PC are reachable from the internet
- Standard Django protections apply (CSRF tokens on forms, ORM parameterized queries — no raw SQL)
