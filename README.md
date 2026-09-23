# Vishwaguru Newspaper Ad Billing System (`vishwaguru-billing`)

An internal advertisement billing, tracking, and PDF generation system for **Vishwaguru Newspaper**.

## 📖 Documentation
- [Project Context](file:///PROJECT_CONTEXT.md): System overview, architecture decisions, and current status.
- [Requirements](file:///REQUIREMENTS.md): Functional and non-functional requirements.
- [High-Level Design (HLD)](file:///HLD.md): Architecture, data flow, and hosting design.
- [Low-Level Design (LLD)](file:///LLD.md): Data models, views, PDF template generation, and calculations.

## 🛠️ Tech Stack
- **Backend:** Python / Django
- **Database:** PostgreSQL (production) / SQLite (development)
- **PDF Engine:** WeasyPrint (HTML/CSS to PDF live on demand — 0 disk files stored)
- **Frontend:** Django Templates + Vanilla JavaScript (live calculations, mobile responsive)
- **Remote Access & Hosting:** Self-hosted on local PC + Cloudflare Tunnel (`cloudflared`) + Gunicorn + Nginx + `systemd`

## 🚀 Key Features
- **Placement Presets:** Quick ad sizing (Front Full, Inside Half, Chouthai, Ear Panel, Custom).
- **Fast PDF Invoicing:** Instant PDF generation with dynamic UPI QR code (`upi://pay?...`) and number-to-words conversion.
- **Client & Verification Tracking:** Store client phone, address, optional GSTIN, and epaper URL + page number.
- **1-Click WhatsApp Share:** Direct WhatsApp Web / Mobile share link with bill summary.
- **Search & Payment Logging:** Filter past bills by client name, phone, bill number, or date range.