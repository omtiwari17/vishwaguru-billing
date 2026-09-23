# Low-Level Design (LLD) — Newspaper Advertisement Billing System

## 1. Data Models

### 1.1 `User` (Django built-in `auth.User`)
Used as-is for staff login. No custom fields needed in v1 — all logged-in staff have equal permissions.

### 1.2 `Bill`

| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| bill_number | CharField, unique | Auto-generated: `VG-YYYY-NNNN` (e.g. `VG-2026-0001`, resets yearly) |
| client_name | CharField | Required |
| client_phone | CharField | Required (used for billing follow-up & 1-click WhatsApp share) |
| client_address | TextField | Optional client address / city |
| client_gstin | CharField | Optional GSTIN / PAN |
| placement_type | CharField (choices) | Front Full, Front Half, Front Chouthai, Inside Full, Inside Half, Inside Chouthai, Back Page, Ear Panel, Custom |
| custom_size_text | CharField | Optional dimensions / description when placement is 'Custom' |
| ad_title | CharField | Optional description, e.g. "Diwali Greetings Ad" |
| edition_date | DateField | Date the ad was printed |
| edition_name | CharField (choices) | e.g. "Indore", "Bhopal", "Ujjain" |
| epaper_link | URLField | Pasted link to the online epaper publication |
| page_number | CharField | Optional page reference (e.g. "Page 1", "Page 4") |
| base_amount | DecimalField | Entered or preset base rate for the placement |
| discount_amount | DecimalField | Optional discount (default 0) |
| total_amount | DecimalField | Calculated: `base_amount - discount_amount` |
| payment_status | CharField (choices) | `Unpaid` / `Paid` / `Partial` |
| amount_paid | DecimalField | Defaults to 0; tracks received amount |
| payment_method | CharField (choices) | `Cash` / `UPI` / `Bank Transfer` / `Cheque` |
| payment_note | CharField | Optional — e.g. cheque number, transaction UTR |
| created_by | ForeignKey → User | Staff member who generated the bill |
| created_at | DateTimeField (auto_now_add) | |

> Note: no `pdf_file` field — PDFs are generated on demand from this row, never stored (see HLD §5).

### 1.3 `PaymentInfo` (single-row config table)

Holds the newspaper's own payment-receiving details, shown on every bill. Set once via Django admin; not re-entered per bill.

| Field | Type |
|---|---|
| bank_name | CharField |
| account_number | CharField |
| ifsc_code | CharField |
| upi_id | CharField |
| account_holder_name | CharField |
| phone_number | CharField |
| office_address | TextField |

## 2. URLs / Views

| URL | View | Purpose |
|---|---|---|
| `/login/` | Django auth login (built-in) | Staff login |
| `/bills/new/` | `BillCreateView` | Form → live calculation → save → redirect to PDF |
| `/bills/<id>/` | `BillDetailView` | View bill details, epaper link, payment status, WhatsApp share button |
| `/bills/<id>/pdf/` | `BillPDFView` | Renders and streams the PDF live (with UPI QR & amount in words) |
| `/bills/search/` | `BillSearchView` | Search box (client name / phone / bill number) + date filter |
| `/bills/<id>/edit-payment/` | `BillPaymentUpdateView` | Update payment status/method after a bill is created |

## 3. PDF Generation

- **Library:** WeasyPrint — renders an HTML/CSS template to PDF
- **Template contents:**
  - Letterhead / Logo image from `billing/static/billing/img/logo.png`
  - Bill number (`VG-YYYY-NNNN`), generation date, edition date
  - Client details: Name, Phone, Address, GSTIN (if provided)
  - Ad details: Placement type, size text, page number, edition
  - Epaper link: Clickable and clearly displayed for verification
  - Financial breakdown: Base Amount, Discount, Net Payable Amount
  - Amount in words: Auto-generated Indian Rupees words via `num2words`
  - Dynamic UPI QR Code: Generated on-demand via `qrcode` library using `upi://pay?pa={upi_id}&pn=Vishwaguru&am={total_amount}&tn={bill_number}`
  - Payment details: Bank name, account number, IFSC, UPI ID
- **Generation trigger:** On every view/download request, not cached or stored on disk

## 4. Amount Calculation Logic

```
total_amount = base_amount - discount_amount
```
- Live client-side JS calculation updates the net total immediately as staff alters rate or discount
- Re-validated/recalculated server-side on submit (never trust client-side math for the saved value)

## 5. Search Implementation

Plain Django ORM filtering:
```python
Bill.objects.filter(
    Q(client_name__icontains=query) |
    Q(client_phone__icontains=query) |
    Q(bill_number__icontains=query),
    edition_date__range=(start_date, end_date)
)
```

Results table columns: bill number, client name, phone, date, placement, amount, payment status, epaper link, PDF link.

## 6. Auth & Permissions
- Django's built-in auth system
- `@login_required` / `LoginRequiredMixin` on every view
- All authenticated staff have equal access (no role tiers in v1)

## 7. UX / Frontend Notes
- **Single-screen bill creation form** grouped visually: Client Details → Placement & Ad → Financials → Payment → Generate
- **Live total calculation** via vanilla JS
- **Dropdown presets** for placements, editions, payment methods, payment statuses
- **1-Click WhatsApp Share** button on detail view (`https://wa.me/{phone}?text={encoded_msg}`)
- **Responsive layout** usable from mobile browser or desktop

## 8. Deployment (Local PC)

- **Production PC:** Ubuntu / Debian Linux PC
- **Stack:** Django + Gunicorn (WSGI) + Nginx (reverse proxy) + PostgreSQL + `cloudflared`
- **Process management:** `systemd` services for auto-start on boot and auto-restart on crash
- **Automated Backup:** Periodic `pg_dump` cron script provided in `deploy/backup.sh`

## 9. Resolved Decisions
All open decisions have been finalized during design interview:
1. Placement presets + custom size supported with base - discount pricing.
2. Bill numbering: `VG-YYYY-NNNN` (resets each calendar year).
3. Vishwaguru logo placed in static assets.
4. Epaper verification combines URL + Page number.
5. Dynamic UPI QR Code embedded directly in the PDF.
6. Local development on Windows, production deployment on Linux with systemd scripts.
