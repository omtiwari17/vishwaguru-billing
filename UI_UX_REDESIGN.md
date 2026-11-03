# UI/UX Improvement Plan

## Audit status - 3 November 2026

This audit covers the repository structure, Django routes/templates, shared CSS, existing screenshots, and the print template. Browser inspection was requested but could not be completed: the browser-control kernel is unavailable in this session because its local assets are missing. Findings marked as source-level have not been presented as browser-tested observations.

### Scope inspected

- Staff routes: dashboard, new bill, bills search, bill detail, UPI verification, payment settings, login, and generated bill output.
- Customer routes: client statement, payment submission, and customer PDF output.
- Shared files: base shell, masthead partial, `style.css`, `calculator.js`, and the bill PDF template.

### Prioritized findings

| Priority | Source-level issue | Result | Improvement |
|---|---|---|---|
| P0 | The shared CSS contains competing size, spacing, and mobile rules; page templates add many inline declarations. | Type, spacing, and control sizes vary from page to page. | Establish one authoritative token/component layer and remove duplicate overrides incrementally. |
| P0 | WeasyPrint is listed as a dependency but is not installed in this local environment. | The bill route falls back to browser print HTML, so PDF output varies by browser and print settings. | Restore/install the expected PDF runtime, then render representative invoices and verify one-page output. |
| P1 | The staff shell and customer portal duplicate responsive and typography rules. | Fixes made in one shell can miss the other. | Share type scale, controls, focus states, and container rules while preserving portal-specific payment layout. |
| P1 | Data-heavy screens combine desktop tables, small inline actions, and partial mobile patterns. | Important bill/payment actions are hard to scan and can be too compact on smaller screens. | Use predictable desktop table actions and compact mobile bill cards with one clear primary action. |
| P1 | New bill and settings forms use long grouped flows plus dense inline styles. | Validation, field hierarchy, and summary information are visually inconsistent. | Standardize form labels, help text, validation, section headers, and sticky summary behavior. |
| P2 | Focus, loading, empty, error, and success states are implemented unevenly. | Keyboard and asynchronous interactions have inconsistent feedback. | Add shared accessible interaction states and test keyboard navigation on each staff workflow. |

### Implementation sequence

1. Establish the shared visual system: typography, spacing, containers, buttons, inputs, panels, tables, badges, and focus states. Do this in the shared stylesheet before changing individual pages.
2. Apply the system to the shell, dashboard, bills/search, and mobile bill cards. Verify visual hierarchy and responsive spacing.
3. Refine bill creation, bill detail, UPI verification, and bank settings without changing forms, endpoints, or business logic.
4. Apply the same readable scale and payment-focused hierarchy to the customer portal.
5. Repair and verify the PDF pipeline with WeasyPrint, then render desktop/browser-print fallback and generated PDFs for paid, unpaid, and partial invoices.
6. Perform browser checks at 1440px, 768px, and 390px: navigation, buttons, validation, search, invoice actions, keyboard focus, and external links.

### Acceptance criteria

- Staff and portal text use a consistent readable scale: standard content 16px, secondary content no smaller than 14px, and clear heading hierarchy.
- Every bordered card, row, and table cell has intentional internal padding at desktop and mobile sizes.
- Dashboard, bill list, form, detail, verification, settings, and customer statement retain all routes and actions.
- The invoice renders as one A4 page for normal invoices, with tested graceful handling for unusually long client or ad details.
- Browser QA documents the actual viewport, interactions checked, and any residual issues.

## Purpose

This document turns the supplied screenshots and the current Django UI into a practical redesign direction for Vishwaguru Ki Jhalak Billing. It is product guidance, not agent workflow guidance, so it belongs here rather than in an `AGENTS.md` file. The screenshots are visual references for the current staff dashboard, bill creation, bill search, UPI verification, bank settings, customer statement portal, and invoice detail screens; their sample customer and financial data must not be reused in demos or documentation.

## Product goals

1. Let staff create a correct bill quickly, with fewer missed fields and a clear running total.
2. Make outstanding balances and payment verification work obvious at a glance.
3. Make every screen comfortable on a phone as well as a desktop, in English and Hindi.
4. Keep customer facing billing pages trustworthy, legible, and easy to pay from.
5. Preserve a restrained newspaper identity while making the application feel like one coherent product.

## What the screenshots show

The screens already have a recognizable identity: warm paper background, Vishwaguru masthead, maroon actions, green paid states, compact tables, and Hindi/English content. The bill form's live invoice summary is a useful pattern, and the statement portal groups overdue and paid invoices in a way customers can understand.

The main opportunity is consistency and hierarchy. Density, type size, spacing, control shape, and panel styling vary between screens. Several screens leave substantial unused space, especially the empty UPI submissions list. Many labels and secondary text are very small. The dashboard combines four metrics, a wide recent-bills table, and lower summary cards without a strong visual distinction between urgent work and general totals. Table actions rely heavily on small icon buttons. The bank settings screen places sensitive account configuration beside an active-credentials preview, so masking and deliberate reveal behavior should be clear. The bill form is long and has many choices; its compact live receipt should stay visible without crowding the fields, especially on smaller screens.

These are design observations from the supplied screenshots and code, not usability test findings. Confirm them with staff before treating any prioritization as measured behavior.

## Design direction

Keep the warm editorial palette and recognizable logo, but use a small, consistent design system. Prefer a clean application surface over a literal newspaper page: generous whitespace, calm card surfaces, clear section titles, and predictable actions. Use maroon for primary actions and selected navigation, green for paid/verified, amber for partial/pending, and red for overdue/destructive states. Never rely on color alone; pair status color with text and, where useful, an icon.

### Foundations

- Define reusable tokens for page background, surface, borders, text, muted text, brand, focus, and status colors. Replace scattered inline colors and repeated style attributes gradually with shared CSS classes.
- Use one spacing scale and one radius/shadow treatment across panels, inputs, buttons, and tables. Keep borders subtle and reserve stronger contrast for focus, selection, and urgency.
- Use Mukta for interface text and Noto Serif Devanagari for editorial headings where it improves identity. Verify glyph coverage, weight, line height, and wrapping for both scripts. Avoid tiny text: target 14–16px for normal labels/body text, with secondary information still comfortably readable.
- Use tabular numerals for rupee amounts, dates, and invoice numbers. Align currency values consistently and show balances with explicit labels.
- Set visible keyboard focus, hover, pressed, disabled, validation, and loading states. Ensure text and controls meet WCAG AA contrast where practical, and make interactive targets about 44px high on touch screens.
- Keep iconography consistent. Icon-only actions need accessible names and an adequate hit area; show text on the most important actions.

## Page-by-page recommendations

### Shared staff navigation

- Keep the logo and primary sections, but make the active location unmistakable with a clear selected treatment and `aria-current="page"`.
- On narrow screens, replace the crowded horizontal tabs with an accessible menu or horizontally scrollable navigation that exposes all destinations. Keep the current page and primary “New bill” action easy to reach.
- Make language selection, signed-in identity, and sign-out visually grouped and keyboard accessible. Avoid tiny links at the far edge of the header.
- Use a consistent content width and page title/action row across staff pages. The current screenshots show different horizontal bounds and header proportions.

### Dashboard

- Lead with a page heading, date context, and one strong “New bill” action. Show a small set of useful totals with consistent labels and number formatting; distinguish today's activity from month-to-date totals.
- Add a prominent actionable “Needs attention” area for overdue balances and pending UPI submissions. Each item should link directly to the relevant client, bill, or verification action.
- Make the recent bills table easier to scan: stable column alignment, readable row spacing, clear paid/partial/unpaid badges, and a predictable actions menu. Keep invoice number and client as the strongest identifiers.
- On mobile, render each bill as a compact card with invoice number, client, amount, balance/status, and a visible primary action; do not squeeze a desktop table into unreadable columns.
- Provide useful empty states and loading feedback for recent bills and summary cards. An empty dashboard should explain the next action and offer bill creation.

### New bill

- Preserve the live invoice summary: it is a strong differentiator. Keep it synchronized with the form and expose the total, received amount, and balance due in a clear hierarchy.
- Organize the form into a short, predictable sequence: client, placement/publication, pricing/payment. Mark required fields consistently and explain optional fields. Consider a compact step/progress indicator only if it reduces perceived length without hiding context.
- Use a responsive two-column layout on desktop, with the receipt sticky only when there is enough vertical space. On mobile, put the summary in a collapsible or compact pinned area that never obscures fields or the submit button.
- Make placement presets visibly selectable, with a clear selected state and readable size labels. Keep custom sizing controls conditional and explain how the selected placement affects price when that is known.
- Surface inline validation next to the relevant field, preserve entered values after errors, and focus or summarize errors on submit. Do not communicate validation only by color.
- Disable duplicate submission while saving, show progress, and give a clear success state with next actions such as open invoice, download PDF, or share statement.
- Keep payment status and payment method controls accessible as real form controls with correct labels and keyboard behavior; decorative pill buttons must update an announced, accessible value.

### Bills and search/filter

- Use a single, prominent search/filter area with clear placeholders and applied-filter chips or a visible summary. Provide a one-click clear-all action.
- Keep date filters understandable in the selected locale and show date format hints. Ensure status filtering works with keyboard and screen readers.
- Use a responsive table on desktop and readable bill cards on mobile. Preserve key identifiers, total, amount received, balance, publication date, and status without horizontal scrolling wherever possible.
- Present “View” as a text-labeled action. Put secondary actions (PDF, WhatsApp, customer portal) in a consistent menu or labeled button group. Add confirmation only for destructive actions.
- Include result count, sort direction, pagination or progressive loading as appropriate, and distinct no-results vs no-bills states. Preserve filters when opening a bill and returning to results.

### Bill detail

- Start with invoice number, status, client, and balance due, followed by a clear action row for PDF, payment update, WhatsApp, and customer portal.
- Group invoice facts, payment summary, and payment history into separate sections with consistent alignment. Make “balance due” the strongest amount when money remains; show a reassuring paid-in-full state when zero.
- Make payment history chronological, readable, and explicit about date, method, reference, and amount. Ensure partial payments are easy to reconcile.
- Keep the customer and public statement link clearly labeled, and provide copy feedback where copying is supported.

### UPI payment verification

- Give each queue tab a count and distinguish pending items from completed history. Pending should be the default when action is required.
- The empty state should occupy the content region purposefully: explain that no submissions need review, show when it was last checked if available, and link to bills/refresh where useful. Avoid a large blank panel with only one line of text.
- In populated rows, make client, amount, UTR, related bill, submitted time, and note easy to scan. Keep Verify and Reject explicit, separated, and keyboard accessible; confirm only where the action is hard to reverse.
- After an action, show a clear result and update counts without losing the user's place.

### Bank and UPI settings

- Separate editable payment configuration from the “currently active” summary. Explain which values appear on invoices and customer statements.
- Mask account numbers by default in summaries and provide a deliberate, labeled reveal/copy action with visible feedback. Never expose full credentials unnecessarily in screenshots, logs, or public-facing pages.
- Validate IFSC, UPI ID, and required bank fields inline. Distinguish unsaved edits from saved active values, with clear Save/Cancel actions and a success confirmation.
- Keep security claims accurate and specific; explain what is encrypted and how users can verify that configuration is saved without relying on decorative security badges.

### Customer statement portal

- Keep the customer experience focused: publisher identity, client name, outstanding balance, a clear “How to pay” action, payment details, and invoice list.
- On mobile, keep the outstanding amount and payment instructions near the top. Use large, readable type and clear tap-to-copy feedback for UPI/bank details.
- Make paid and outstanding bills visually distinct and explain how a customer can report a transfer, including expected response/verification where the product supports it.
- Clearly label PDF and epaper links, use safe external-link behavior, and provide a helpful state for expired or invalid portal links.

## Responsive and accessibility requirements

- Design mobile first at 320px and verify key workflows at phone, tablet, and desktop widths. Avoid horizontal page scrolling; for genuinely wide data, provide a deliberate contained scroll region with a visible cue.
- Support keyboard-only use, visible focus, semantic headings, form labels, table headers, button names, and screen-reader announcements for async updates and validation results.
- Check Hindi and English at realistic long strings, including buttons, dates, currency, client names, and error messages. Avoid fixed widths that clip Devanagari text.
- Respect reduced-motion preferences. Keep animation brief and functional; do not make status meaning depend on motion.
- Provide empty, loading, error, success, disabled, and permission-denied states for each data-heavy workflow.

## Delivery sequence

### P0: Consistency and legibility

1. Consolidate repeated inline styles into shared tokens/components for typography, spacing, buttons, fields, cards, tables, and status badges.
2. Improve small text, control height, focus styles, and bilingual wrapping across all screens.
3. Fix high-impact empty states and make primary page actions consistent.

### P1: Core staff workflows

1. Refine bill creation hierarchy, validation, submission feedback, and responsive live summary.
2. Improve bill search, result scanning, responsive rows/cards, and consistent action placement.
3. Promote overdue accounts and pending payment verification as direct dashboard tasks.

### P2: Customer confidence and administration

1. Polish invoice detail and payment history for reconciliation.
2. Improve customer statement payment guidance and mobile readability.
3. Clarify bank settings save/reveal behavior and mask sensitive values by default.

## How to evaluate the redesign

Before visual polish is considered complete, walk through these tasks with staff using English and Hindi and at phone and desktop sizes:

- Create a paid, unpaid, and partial-payment bill, including a validation error and a custom placement.
- Find an invoice by client, invoice number, status, and date range; open it and return without losing filters.
- Identify the next overdue account and review a pending UPI submission.
- Open a customer statement on a phone, find the due amount, copy payment details, and open an invoice PDF.
- Update bank details and confirm which values are active and which are masked.

Record completion, errors, and points of hesitation. Prioritize changes that reduce incorrect amounts/statuses, missed verification, and time spent finding the right bill. Keep the design lightweight and consistent with the existing Django templates and vanilla JavaScript; avoid introducing a frontend framework solely for visual polish.

## Existing implementation references

- Shared staff shell and typography: `billing/templates/billing/base.html`, `billing/templates/billing/partials/_masthead.html`, `billing/static/billing/css/style.css`
- Dashboard and recent bill list: `billing/templates/billing/dashboard.html`, `billing/templates/billing/partials/bills_table.html`, `billing/templates/billing/partials/stats_strip.html`
- Bill creation and live summary: `billing/templates/billing/bill_form.html`, `billing/static/billing/js/calculator.js`
- Search, detail, and verification: `billing/templates/billing/bill_search.html`, `billing/templates/billing/bill_detail.html`, `billing/templates/billing/payment_submissions_list.html`
- Settings and customer portal: `billing/templates/billing/payment_info_settings.html`, `billing/templates/billing/customer_portal.html`
