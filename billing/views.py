import logging
logger = logging.getLogger(__name__)
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import render_to_string
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from django.utils import timezone
from billing.templatetags.billing_tags import indian_currency

from billing.models import (
    Bill,
    PaymentInfo,
    PaymentStatus,
    PAYMENT_STATUS_CHOICES_HI,
    Client,
    PaymentSubmission,
    PaymentMethod,
)
from billing.forms import (
    RecordPaymentForm,
    BillForm,
    BillPaymentUpdateForm,
    CustomerPaymentSubmissionForm,
    BillForm,
    BillPaymentUpdateForm,
    CustomerPaymentSubmissionForm,
    PaymentInfoForm,

)
from billing.translator import (
    translate_text,
    detect_script,
    is_devanagari,
    make_bilingual,
    split_bilingual,
)
from billing.utils import (
    generate_bill_number,
    generate_upi_qr_base64,
    get_upi_intent_url,
    amount_in_words_bilingual,
)


def _disable_response_cache(response):
    """Prevent browsers and proxies from reusing stale generated invoice PDFs."""
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@login_required
def dashboard(request):
    """
    Main Management & Operations Dashboard for Vishwaguru Billing.
    Displays financial KPIs, today's metrics, monthly totals,
    recent invoices, pending UPI verifications, and overdue client follow-ups.
    """
    site_lang = request.session.get('site_lang', 'en')
    today = timezone.localdate()

    # 1. Today's Statistics
    today_bills = Bill.objects.filter(created_at__date=today)
    today_stats = today_bills.aggregate(
        count=Count('id'),
        billed=Sum('total_amount'),
        paid=Sum('amount_paid'),
    )
    today_count = today_stats['count'] or 0
    today_billed = today_stats['billed'] or Decimal('0.00')
    today_paid = today_stats['paid'] or Decimal('0.00')
    today_pending = max(Decimal('0.00'), today_billed - today_paid)

    # 2. Current Month's Statistics
    month_bills = Bill.objects.filter(
        created_at__year=today.year,
        created_at__month=today.month,
    )
    month_stats = month_bills.aggregate(
        count=Count('id'),
        billed=Sum('total_amount'),
        paid=Sum('amount_paid'),
    )
    month_count = month_stats['count'] or 0
    month_billed = month_stats['billed'] or Decimal('0.00')
    month_paid = month_stats['paid'] or Decimal('0.00')
    month_pending = max(Decimal('0.00'), month_billed - month_paid)

    # 3. All-time Financial Aggregate
    all_stats = Bill.objects.aggregate(
        total_count=Count('id'),
        total_billed=Sum('total_amount'),
        total_collected=Sum('amount_paid'),
    )
    total_count = all_stats['total_count'] or 0
    total_billed = all_stats['total_billed'] or Decimal('0.00')
    total_collected = all_stats['total_collected'] or Decimal('0.00')
    total_outstanding = max(Decimal('0.00'), total_billed - total_collected)

    # 4. Payment Status Breakdown
    status_counts = Bill.objects.values('payment_status').annotate(
        count=Count('id'),
        amount=Sum('total_amount'),
    )
    status_summary = {
        'Paid': {'count': 0, 'amount': Decimal('0.00')},
        'Unpaid': {'count': 0, 'amount': Decimal('0.00')},
        'Partial': {'count': 0, 'amount': Decimal('0.00')},
    }
    for item in status_counts:
        st = item['payment_status']
        if st in status_summary:
            status_summary[st]['count'] = item['count']
            status_summary[st]['amount'] = item['amount'] or Decimal('0.00')

    if total_count > 0:
        paid_pct = round((status_summary['Paid']['count'] / total_count) * 100)
        partial_pct = round((status_summary['Partial']['count'] / total_count) * 100)
        unpaid_pct = max(0, 100 - paid_pct - partial_pct)
    else:
        paid_pct, partial_pct, unpaid_pct = 0, 0, 0
    status_summary['Paid']['pct'] = paid_pct
    status_summary['Partial']['pct'] = partial_pct
    status_summary['Unpaid']['pct'] = unpaid_pct

    unpaid_bills_count = status_summary['Unpaid']['count'] + status_summary['Partial']['count']

    # 5. Customer UPI Payment Submissions Pending Verification
    pending_submissions = PaymentSubmission.objects.filter(
        status='pending'
    ).select_related('client', 'bill').order_by('-submitted_at')
    pending_submissions_count = pending_submissions.count()

    # 6. Recent Bills (latest 10 or search query & status filter)
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'ALL').strip().upper()
    bills_qs = Bill.objects.select_related('client', 'created_by')

    if query:
        bills_qs = bills_qs.filter(
            Q(client_name__icontains=query) |
            Q(client_phone__icontains=query) |
            Q(bill_number__icontains=query) |
            Q(ad_title__icontains=query)
        )

    if status_filter in ['PAID', 'PARTIAL', 'UNPAID']:
        bills_qs = bills_qs.filter(payment_status__iexact=status_filter)

    limit = 20 if (query or status_filter != 'ALL') else 10
    recent_bills = bills_qs.order_by('-created_at')[:limit]

    # 7. Top Clients with Outstanding Balance (for quick 1-click WhatsApp reminders)
    clients_with_due = Client.objects.all()
    debtors = []
    for c in clients_with_due:
        due = c.total_outstanding
        if due > Decimal('0.00'):
            debtors.append({
                'client': c,
                'outstanding': due,
                'unpaid_count': len(c.get_unpaid_bills()),
                'whatsapp_url': c.get_whatsapp_portal_share_url(request),
            })
    debtors.sort(key=lambda x: x['outstanding'], reverse=True)
    top_debtors = debtors[:5]

    # 8. Edition Breakdown (Top active editions)
    edition_stats = Bill.objects.values('edition_name').annotate(
        count=Count('id'),
        total=Sum('total_amount'),
    ).order_by('-count')[:5]

    payment_info = PaymentInfo.get_solo()

    context = {
        'site_lang': site_lang,
        'today': today,
        'today_count': today_count,
        'today_billed': today_billed,
        'today_paid': today_paid,
        'today_pending': today_pending,
        'month_count': month_count,
        'month_billed': month_billed,
        'month_paid': month_paid,
        'month_pending': month_pending,
        'total_count': total_count,
        'total_billed': total_billed,
        'total_collected': total_collected,
        'total_outstanding': total_outstanding,
        'status_summary': status_summary,
        'unpaid_bills_count': unpaid_bills_count,
        'pending_submissions_count': pending_submissions_count,
        'pending_submissions': pending_submissions[:5],
        'recent_bills': recent_bills,
        'top_debtors': top_debtors,
        'edition_stats': edition_stats,
        'payment_info': payment_info,
        'title': 'डैशबोर्ड | विश्वगुरु विज्ञापन बिलिंग' if site_lang == 'hi' else 'Dashboard | Vishwaguru Billing',
        'query': query,
        'status_filter': status_filter,
    }
    if request.headers.get('HX-Request') and ('q' in request.GET or 'status' in request.GET):
        return render(request, 'billing/partials/bills_table.html', context)
    return render(request, 'billing/dashboard.html', context)


@login_required
def bill_create(request):
    """
    Create a new advertisement bill.
    Live total calculation happens client-side, recalculated server-side.
    """
    site_lang = request.session.get('site_lang', 'en')

    if request.method == 'POST':
        form = BillForm(request.POST, site_lang=site_lang)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.created_by = request.user
            bill.bill_number = generate_bill_number()

            # Process bilingual translation for client_name, client_address, ad_title
            client_name_trans = request.POST.get('client_name_trans', '').strip()
            client_address_trans = request.POST.get('client_address_trans', '').strip()
            ad_title_trans = request.POST.get('ad_title_trans', '').strip()

            def _combine_bilingual_field(raw_val: str, trans_val: str) -> str:
                raw = (raw_val or '').strip()
                trans = (trans_val or '').strip()
                if not raw:
                    return ''
                if not trans:
                    return make_bilingual(raw)
                hi_raw, en_raw = split_bilingual(raw)
                if hi_raw and en_raw:
                    if is_devanagari(trans):
                        return make_bilingual('', custom_hi=trans, custom_en=en_raw)
                    else:
                        return make_bilingual('', custom_hi=hi_raw, custom_en=trans)
                if is_devanagari(raw):
                    return make_bilingual('', custom_hi=raw, custom_en=trans)
                else:
                    return make_bilingual('', custom_hi=trans, custom_en=raw)

            if 'client_name_trans' in request.POST:
                bill.client_name = _combine_bilingual_field(bill.client_name, client_name_trans)
            if 'client_address_trans' in request.POST:
                bill.client_address = _combine_bilingual_field(bill.client_address, client_address_trans)
            if 'ad_title_trans' in request.POST:
                bill.ad_title = _combine_bilingual_field(bill.ad_title, ad_title_trans)

            # Automatically remember / update client master record & link to bill
            if bill.client_name:
                client_obj, _ = Client.objects.update_or_create(
                    name=bill.client_name.strip(),
                    defaults={
                        'phone': bill.client_phone or '',
                        'address': bill.client_address or '',
                        'gstin': bill.client_gstin or '',
                    }
                )
                bill.client = client_obj

            bill.save()

            msg = (
                f"बिल सफलतापूर्वक बनाया गया! बिल क्रमांक: {bill.bill_number}"
                if site_lang == 'hi'
                else f"Bill created successfully! Invoice No: {bill.bill_number}"
            )
            messages.success(request, msg)
            return redirect('billing:bill_detail', pk=bill.pk)
    else:
        form = BillForm(site_lang=site_lang)

    # Today's quick dashboard statistics
    today = timezone.localdate()
    today_bills = Bill.objects.filter(created_at__date=today)
    today_stats = today_bills.aggregate(
        count=Count('id'),
        billed=Sum('total_amount'),
        paid=Sum('amount_paid'),
    )
    today_count = today_stats['count'] or 0
    today_billed = today_stats['billed'] or Decimal('0.00')
    today_paid = today_stats['paid'] or Decimal('0.00')
    today_pending = max(Decimal('0.00'), today_billed - today_paid)

    # 5 Most recent bills for quick-access drawer
    recent_bills = Bill.objects.select_related('created_by').order_by('-created_at')[:5]

    payment_info = PaymentInfo.get_solo()
    context = {
        'form': form,
        'payment_info': payment_info,
        'title': 'नया विज्ञापन बिल बनाएं' if site_lang == 'hi' else 'Create Advertisement Bill',
        'today_count': today_count,
        'today_billed': today_billed,
        'today_paid': today_paid,
        'today_pending': today_pending,
        'recent_bills': recent_bills,
    }
    return render(request, 'billing/bill_form.html', context)


def get_bill_payment_history(bill):
    """
    Return a unified chronological list of payments recorded for this bill.
    Each item is a dict: date, method, reference, amount, note.
    """
    submissions = bill.payment_submissions.filter(status='verified').order_by('submitted_at')
    items = []
    recorded_sum = Decimal('0.00')
    for sub in submissions:
        items.append({
            'date': sub.verified_at or sub.submitted_at,
            'method': sub.payment_method,
            'reference': sub.utr_number,
            'amount': sub.amount,
            'note': sub.notes,
        })
        recorded_sum += sub.amount

    # If bill had an initial payment at creation time that isn't in submissions
    if bill.amount_paid > recorded_sum:
        initial_payment = bill.amount_paid - recorded_sum
        items.insert(0, {
            'date': bill.created_at,
            'method': bill.payment_method or 'Initial Payment',
            'reference': bill.payment_note or '-',
            'amount': initial_payment,
            'note': 'Initial payment on bill creation' if bill.bill_language == 'en' else 'बिल निर्माण के समय दर्ज भुगतान',
        })
    return items


@login_required
def bill_detail(request, pk):
    """
    Display complete bill details, payment actions, and WhatsApp share button.
    Includes customer portal statement link and checks for client payment submissions.
    """
    bill = get_object_or_404(Bill, pk=pk)
    payment_info = PaymentInfo.get_solo()
    amount_words = amount_in_words_bilingual(bill.total_amount)

    qr_code_base64 = generate_upi_qr_base64(
        upi_id=payment_info.upi_id,
        payee_name=payment_info.account_holder_name or payment_info.newspaper_name,
        amount=bill.balance_amount if bill.balance_amount > 0 else bill.total_amount,
        bill_number_or_note=bill.bill_number,
    )

    # Pending submissions from customer for this bill or client
    pending_submissions = []
    client_obj = bill.client
    if not client_obj and bill.client_name:
        client_obj, _ = Client.objects.get_or_create(
            name=bill.client_name.strip(),
            defaults={
                'phone': bill.client_phone or '',
                'address': bill.client_address or '',
                'gstin': bill.client_gstin or '',
            }
        )
        if not bill.client:
            bill.client = client_obj
            bill.save(update_fields=['client'])

    if client_obj:
        pending_submissions = client_obj.payment_submissions.filter(status='pending')

    site_lang = request.session.get('site_lang', 'en')
    payment_history = get_bill_payment_history(bill)
    record_form = RecordPaymentForm(bill=bill, site_lang=site_lang) if bill.balance_amount > Decimal('0.00') else None

    context = {
        'bill': bill,
        'client': client_obj,
        'payment_info': payment_info,
        'amount_words': amount_words,
        'qr_code_base64': qr_code_base64,
        'record_form': record_form,
        'payment_form': BillPaymentUpdateForm(instance=bill, site_lang=site_lang),
        'payment_history': payment_history,
        'pending_submissions': pending_submissions,
        'portal_url': client_obj.get_portal_url(request) if client_obj else "",
        'whatsapp_portal_share_url': client_obj.get_whatsapp_portal_share_url(request) if client_obj else "",
        'title': f"{bill.bill_number} | विश्वगुरु बिलिंग" if site_lang == 'hi' else f"{bill.bill_number} | Vishwaguru Billing",
    }
    return render(request, 'billing/bill_detail.html', context)



@login_required
def bill_pdf_view(request, pk):
    """
    Render and stream the PDF live on-demand using WeasyPrint.
    PDFs are never stored on disk.
    """
    bill = get_object_or_404(Bill, pk=pk)
    payment_info = PaymentInfo.get_solo()
    amount_words = amount_in_words_bilingual(bill.total_amount)

    # Dynamic UPI QR code for remaining balance or total amount
    payable_for_qr = bill.balance_amount if bill.balance_amount > 0 else bill.total_amount
    qr_code_base64 = generate_upi_qr_base64(
        upi_id=payment_info.upi_id,
        payee_name=payment_info.account_holder_name or payment_info.newspaper_name,
        amount=payable_for_qr,
        bill_number=bill.bill_number,
    )

    # Determine PDF language: from URL param if present, or bill's own setting, default 'en'
    req_lang = request.GET.get('lang', '').strip().lower()
    if req_lang in ('hi', 'hindi'):
        pdf_lang = 'hi'
    elif req_lang in ('en', 'english'):
        pdf_lang = 'en'
    else:
        pdf_lang = 'hi' if getattr(bill, 'bill_language', 'en') == 'hi' else 'en'

    # Signature mode: '0' for computer generated (no sign required, default), '1' for physical seal & sign line
    require_sign = request.GET.get('sign', '0').lower() in ('1', 'true', 'yes', 'seal', 'manual')

    context = {
        'bill': bill,
        'payment_info': payment_info,
        'amount_words': amount_words,
        'qr_code_base64': qr_code_base64,
        'pdf_lang': pdf_lang,
        'require_sign': require_sign,
        'request': request,
    }

    html_content = render_to_string('billing/bill_pdf.html', context, request=request)

    try:
        from weasyprint import HTML
        base_url = request.build_absolute_uri('/')
        pdf_file = HTML(string=html_content, base_url=base_url).write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        filename = f"{bill.bill_number}.pdf"

        # If user explicitly asked for download, set attachment header
        if request.GET.get('download') == '1':
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        else:
            response['Content-Disposition'] = f'inline; filename="{filename}"'

        return _disable_response_cache(response)
    except Exception as e:
        # Fallback for environments where WeasyPrint native C-libraries are missing
        # Log real error on server and show a friendly line to user
        logger.warning("WeasyPrint PDF generation failed: %s", e, exc_info=True)
        msg = (
            "पीडीएफ तैयार नहीं किया जा सका। इसके स्थान पर प्रिंट दृश्य दिखाया जा रहा है।"
            if request.session.get('site_lang') == 'hi'
            else "PDF could not be generated. Showing the print view instead."
        )
        messages.warning(request, msg)
        return _disable_response_cache(render(request, 'billing/bill_pdf.html', context))


@login_required
def bill_search(request):
    """
    Search and filter past bills by client name, phone, bill number, and date range.
    Includes aggregated metrics for management.
    """
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()

    bills = Bill.objects.all()

    if query:
        bills = bills.filter(
            Q(client_name__icontains=query) |
            Q(client_phone__icontains=query) |
            Q(bill_number__icontains=query) |
            Q(ad_title__icontains=query)
        )

    if status:
        bills = bills.filter(payment_status=status)

    if start_date:
        bills = bills.filter(edition_date__gte=start_date)

    if end_date:
        bills = bills.filter(edition_date__lte=end_date)

    # Aggregates for financial summary cards
    stats = bills.aggregate(
        total_count=Count('id'),
        total_billed=Sum('total_amount'),
        total_collected=Sum('amount_paid'),
    )

    total_billed = stats['total_billed'] or Decimal('0.00')
    total_collected = stats['total_collected'] or Decimal('0.00')
    total_outstanding = max(Decimal('0.00'), total_billed - total_collected)

    paginator = Paginator(bills, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    site_lang = request.session.get('site_lang', 'en')
    status_choices = PAYMENT_STATUS_CHOICES_HI if site_lang == 'hi' else PaymentStatus.choices

    context = {
        'bills': page_obj,
        'page_obj': page_obj,
        'query': query,
        'status': status,
        'start_date': start_date,
        'end_date': end_date,
        'status_choices': status_choices,
        'total_count': stats['total_count'] or 0,
        'total_billed': total_billed,
        'total_collected': total_collected,
        'total_outstanding': total_outstanding,
        'title': 'बिल खोजें व विवरण' if site_lang == 'hi' else 'Search Invoices & Bills',
    }
    return render(request, 'billing/bill_search.html', context)


@login_required
def bill_payment_update(request, pk):
    """
    Endpoint to record payment for a bill. Supports HTMX in-place updates.
    """
    site_lang = request.session.get('site_lang', 'en')
    bill = get_object_or_404(Bill, pk=pk)

    # Ensure client exists and is linked
    if not bill.client and bill.client_name:
        client_obj, _ = Client.objects.get_or_create(
            name=bill.client_name.strip(),
            defaults={
                'phone': bill.client_phone or '',
                'address': bill.client_address or '',
                'gstin': bill.client_gstin or '',
            }
        )
        bill.client = client_obj
        bill.save(update_fields=['client'])

    is_htmx = bool(request.headers.get('HX-Request'))

    if request.method == 'POST':
        # Check if submitted form is RecordPaymentForm (new desk flow)
        if 'amount' in request.POST and ('payment_method' in request.POST or 'reference' in request.POST):
            form = RecordPaymentForm(request.POST, bill=bill, site_lang=site_lang)
            if form.is_valid():
                amount = form.cleaned_data['amount']
                method = form.cleaned_data['payment_method']
                reference = form.cleaned_data.get('reference', '')
                note = form.cleaned_data.get('note', '')

                # 1. Create verified PaymentSubmission record
                if bill.client:
                    PaymentSubmission.objects.create(
                        client=bill.client,
                        bill=bill,
                        amount=amount,
                        utr_number=reference or ('Cash' if method == 'Cash' else '-'),
                        payment_method=method,
                        notes=note or '',
                        status='verified',
                        verified_at=timezone.now(),
                        verified_by=request.user if request.user.is_authenticated else None,
                    )

                # 2. Update Bill financials
                bill.amount_paid += amount
                bill.payment_method = method
                if reference:
                    bill.payment_note = reference
                if bill.balance_amount <= Decimal('0.00'):
                    bill.payment_status = PaymentStatus.PAID
                else:
                    bill.payment_status = PaymentStatus.PARTIAL
                bill.save()

                # Refresh from DB
                bill.refresh_from_db()

                formatted_amt = indian_currency(amount)
                success_msg = (
                    f"{formatted_amt} का भुगतान सफलतापूर्वक दर्ज किया गया।"
                    if site_lang == 'hi'
                    else f"Payment of {formatted_amt} recorded successfully."
                )

                if is_htmx:
                    payment_history = get_bill_payment_history(bill)
                    new_record_form = RecordPaymentForm(bill=bill, site_lang=site_lang) if bill.balance_amount > Decimal('0.00') else None
                    portal_url = bill.client.get_portal_url(request) if bill.client else ""
                    ctx = {
                        'bill': bill,
                        'record_form': new_record_form,
                        'payment_history': payment_history,
                        'portal_url': portal_url,
                        'payment_success_msg': success_msg,
                        'site_lang': site_lang,
                        'pending_submissions': bill.client.payment_submissions.filter(status='pending') if bill.client else [],
                    }
                    return render(request, 'billing/partials/bill_detail_pane.html', ctx)

                messages.success(request, success_msg)
                return redirect('billing:bill_detail', pk=bill.pk)
            else:
                # Form has validation errors
                payment_history = get_bill_payment_history(bill)
                portal_url = bill.client.get_portal_url(request) if bill.client else ""
                ctx = {
                    'bill': bill,
                    'record_form': form,
                    'payment_history': payment_history,
                    'portal_url': portal_url,
                    'site_lang': site_lang,
                    'pending_submissions': bill.client.payment_submissions.filter(status='pending') if bill.client else [],
                }
                if is_htmx:
                    return render(request, 'billing/partials/bill_detail_pane.html', ctx, status=200)

                return render(request, 'billing/bill_detail.html', ctx)

        # Legacy BillPaymentUpdateForm fallback
        legacy_form = BillPaymentUpdateForm(request.POST, instance=bill, site_lang=site_lang)
        if legacy_form.is_valid():
            legacy_form.save()
            msg = (
                f"बिल {bill.bill_number} की भुगतान स्थिति अपडेट कर दी गई है।"
                if site_lang == 'hi'
                else f"Payment status for bill {bill.bill_number} updated successfully."
            )
            messages.success(request, msg)

    return redirect('billing:bill_detail', pk=bill.pk)


def set_site_language(request, lang_code):
    """
    Switch interface language between English ('en') and Hindi ('hi').
    """
    if lang_code in ('en', 'hi'):
        request.session['site_lang'] = lang_code
    referer = request.META.get('HTTP_REFERER') or '/bills/new/'
    return redirect(referer)


@login_required
def client_search_api(request):
    """
    API endpoint for client autocomplete and pending balance lookup.
    Returns matching client profiles with phone, address, GSTIN, and old pending balance.
    """
    q = request.GET.get('q', '').strip()
    if not q:
        clients = Client.objects.all().order_by('-updated_at')[:10]
    else:
        clients = Client.objects.filter(
            Q(name__icontains=q) | Q(phone__icontains=q)
        ).order_by('name')[:15]

    data = []
    for c in clients:
        unpaid_bills = Bill.objects.filter(
            client_name__iexact=c.name,
            payment_status__in=[PaymentStatus.UNPAID, PaymentStatus.PARTIAL]
        )
        total_pending = sum((b.balance_amount for b in unpaid_bills), Decimal('0.00'))
        data.append({
            'id': c.id,
            'name': c.name,
            'phone': c.phone,
            'address': c.address,
            'gstin': c.gstin,
            'pending_due': float(total_pending),
        })

    return JsonResponse({'clients': data})


@login_required
def api_translate(request):
    """
    Lightweight API endpoint for live on-the-fly translation of bill form inputs
    (client name, address, ad title) between Hindi and English.
    """
    text = (request.GET.get('text') or request.POST.get('text', '')).strip()
    if not text:
        return JsonResponse({'original': '', 'translated': '', 'detected_script': 'en'})

    source_lang = request.GET.get('sl') or request.POST.get('sl', 'auto')
    target_lang = request.GET.get('tl') or request.POST.get('tl', None)

    translated = translate_text(text, source_lang=source_lang, target_lang=target_lang)
    detected = detect_script(text)
    suggested_target = 'en' if detected == 'hi' else 'hi'

    return JsonResponse({
        'original': text,
        'translated': translated,
        'detected_script': detected,
        'target_lang': target_lang or suggested_target,
    })


def customer_portal(request, token):
    """
    Public, secure, tokenized statement portal for customers.
    Shows complete advertisement ledger: which ads are unpaid/due, which are paid,
    total outstanding balance, zero-fee direct UPI payment intent & QR code,
    and a UTR verification submission form.
    """
    client = get_object_or_404(Client, access_token=token)
    lang = request.GET.get('lang', 'hi')
    if lang not in ('en', 'hi'):
        lang = 'hi'

    payment_info = PaymentInfo.get_solo()
    all_bills = client.get_all_bills()
    unpaid_bills = client.get_unpaid_bills()
    paid_bills = client.get_paid_bills()

    total_billed = client.total_billed
    total_paid = client.total_paid
    total_outstanding = client.total_outstanding

    # Direct UPI Intent link and QR Code for total outstanding balance
    payee_name = payment_info.account_holder_name or payment_info.newspaper_name
    upi_total_intent = ""
    upi_total_qr = None
    if total_outstanding > Decimal('0.00'):
        clean_name = client.name.replace('&', 'and')
        upi_total_intent = get_upi_intent_url(
            upi_id=payment_info.upi_id,
            payee_name=payee_name,
            amount=total_outstanding,
            transaction_note=f"VG Dues {clean_name[:15]}"
        )
        upi_total_qr = generate_upi_qr_base64(
            upi_id=payment_info.upi_id,
            payee_name=payee_name,
            amount=total_outstanding,
            bill_number_or_note=f"VG Dues - {clean_name}"
        )

    # Attach UPI intent and QR to individual unpaid bills
    for b in unpaid_bills:
        b.upi_intent = get_upi_intent_url(
            upi_id=payment_info.upi_id,
            payee_name=payee_name,
            amount=b.balance_amount,
            transaction_note=f"{b.bill_number}"
        )
        b.upi_qr = generate_upi_qr_base64(
            upi_id=payment_info.upi_id,
            payee_name=payee_name,
            amount=b.balance_amount,
            bill_number_or_note=b.bill_number
        )

    # Pending UTR submissions from client awaiting staff review
    pending_submissions = client.payment_submissions.filter(status='pending')

    submission_form = CustomerPaymentSubmissionForm(
        client=client,
        lang=lang,
        initial={'amount': total_outstanding if total_outstanding > 0 else ''}
    )

    context = {
        'client': client,
        'payment_info': payment_info,
        'all_bills': all_bills,
        'unpaid_bills': unpaid_bills,
        'paid_bills': paid_bills,
        'total_billed': total_billed,
        'total_paid': total_paid,
        'total_outstanding': total_outstanding,
        'upi_total_intent': upi_total_intent,
        'upi_total_qr': upi_total_qr,
        'pending_submissions': pending_submissions,
        'submission_form': submission_form,
        'lang': lang,
    }
    return render(request, 'billing/customer_portal.html', context)


def customer_portal_short(request, token):
    """
    Short URL redirect: /c/<uuid:token>/ -> /statement/<uuid:token>/
    """
    lang = request.GET.get('lang', '')
    url = redirect('billing:customer_portal', token=token).url
    if lang:
        url = f"{url}?lang={lang}"
    return redirect(url)


def customer_payment_submit(request, token):
    """
    Handles customer UTR submission from the public statement portal.
    """
    client = get_object_or_404(Client, access_token=token)
    lang = request.GET.get('lang', 'hi')

    if request.method == 'POST':
        form = CustomerPaymentSubmissionForm(request.POST, client=client, lang=lang)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.client = client
            sub.status = 'pending'
            sub.save()

            if lang == 'hi':
                msg = f"धन्यवाद! आपका यूटीआर संदर्भ क्रमांक ({sub.utr_number}) सफलतापूर्वक दर्ज हो गया है। सत्यापन के बाद आपका खाता स्वतः अद्यतन हो जाएगा।"
            else:
                msg = f"Thank you! Your payment reference ({sub.utr_number}) has been submitted. Our accounts team will verify and update your statement shortly."
            messages.success(request, msg)
            if request.headers.get('HX-Request'):
                return render(request, 'billing/partials/utr_submitted.html', {
                    'submission': sub,
                    'lang': lang,
                })
        else:
            if request.headers.get('HX-Request'):
                return render(request, 'billing/partials/utr_form.html', {
                    'client': client,
                    'submission_form': form,
                    'lang': lang,
                    'total_outstanding': client.total_outstanding,
                })
            if lang == 'hi':
                messages.error(request, "कृपया सही राशि और यूटीआर संख्या दर्ज करें।")
            else:
                messages.error(request, "Please enter a valid amount and UTR reference number.")

    return redirect(f"{client.get_portal_url()}?lang={lang}")


def customer_bill_pdf(request, token, bill_id):
    """
    Allows a customer to download/view their bill PDF via their secure token
    without needing staff login credentials.
    """
    client = get_object_or_404(Client, access_token=token)
    bill = get_object_or_404(
        Bill.objects.filter(
            Q(client=client) | Q(client_name__iexact=client.name)
        ),
        pk=bill_id
    )

    payment_info = PaymentInfo.get_solo()
    amount_words = amount_in_words_bilingual(bill.total_amount)
    payable_for_qr = bill.balance_amount if bill.balance_amount > 0 else bill.total_amount
    qr_code_base64 = generate_upi_qr_base64(
        upi_id=payment_info.upi_id,
        payee_name=payment_info.account_holder_name or payment_info.newspaper_name,
        amount=payable_for_qr,
        bill_number_or_note=bill.bill_number,
    )

    req_lang = request.GET.get('lang', '').strip().lower()
    if req_lang in ('hi', 'hindi'):
        pdf_lang = 'hi'
    elif req_lang in ('en', 'english'):
        pdf_lang = 'en'
    else:
        pdf_lang = 'hi' if getattr(bill, 'bill_language', 'en') == 'hi' else 'en'
    require_sign = request.GET.get('sign', '0').lower() in ('1', 'true', 'yes', 'seal', 'manual')

    context = {
        'bill': bill,
        'payment_info': payment_info,
        'amount_words': amount_words,
        'qr_code_base64': qr_code_base64,
        'pdf_lang': pdf_lang,
        'require_sign': require_sign,
        'request': request,
    }

    html_content = render_to_string('billing/bill_pdf.html', context, request=request)

    try:
        from weasyprint import HTML
        base_url = request.build_absolute_uri('/')
        pdf_file = HTML(string=html_content, base_url=base_url).write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        filename = f"{bill.bill_number}.pdf"
        if request.GET.get('download') == '1':
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        else:
            response['Content-Disposition'] = f'inline; filename="{filename}"'
        return _disable_response_cache(response)
    except Exception as e:
        logger.warning('WeasyPrint PDF generation failed in customer_bill_pdf: %s', e, exc_info=True)
        return _disable_response_cache(render(request, 'billing/bill_pdf.html', context))


@login_required
def verify_payment_submission(request, submission_id):
    """
    Staff action to verify or reject a customer payment submission.
    """
    submission = get_object_or_404(PaymentSubmission, pk=submission_id)
    action = request.POST.get('action', 'verify')
    site_lang = request.session.get('site_lang', 'en')

    if action == 'verify':
        submission.status = 'verified'
        submission.verified_at = timezone.now()
        submission.verified_by = request.user
        submission.save()

        # Apply payment to bill
        bill = submission.bill
        if not bill:
            unpaid = submission.client.get_unpaid_bills()
            bill = unpaid[0] if unpaid else None

        if bill:
            bill.amount_paid = (bill.amount_paid or Decimal('0.00')) + submission.amount
            if bill.amount_paid >= bill.total_amount:
                bill.payment_status = PaymentStatus.PAID
            else:
                bill.payment_status = PaymentStatus.PARTIAL
            bill.payment_method = PaymentMethod.UPI
            note_suffix = f"Portal UTR: {submission.utr_number}"
            bill.payment_note = f"{bill.payment_note}; {note_suffix}" if bill.payment_note else note_suffix
            bill.save()

        msg = (
            f"यूटीआर {submission.utr_number} (₹{submission.amount}) सत्यापित कर दिया गया है।"
            if site_lang == 'hi'
            else f"UTR {submission.utr_number} for ₹{submission.amount} has been verified and applied to bill."
        )
        messages.success(request, msg)

    elif action == 'reject':
        submission.status = 'rejected'
        submission.verified_at = timezone.now()
        submission.verified_by = request.user
        submission.save()

        msg = (
            f"यूटीआर {submission.utr_number} अस्वीकृत कर दिया गया है।"
            if site_lang == 'hi'
            else f"Payment submission {submission.utr_number} was rejected."
        )
        messages.warning(request, msg)

    if request.headers.get('HX-Request'):
        pending_count = PaymentSubmission.objects.filter(status='pending').count()
        context = {
            'submission': submission,
            'site_lang': site_lang,
            'pending_submissions_count': pending_count,
            'message': msg,
        }
        return render(request, 'billing/partials/submission_row_verified.html', context)

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/bills/search/'
    return redirect(next_url)


@login_required
def payment_submissions_list(request):
    """
    Staff view to review all customer payment submissions.
    """
    status_filter = request.GET.get('status', 'pending')
    all_submissions = PaymentSubmission.objects.all()
    submission_counts = all_submissions.aggregate(
        pending_count=Count('id', filter=Q(status='pending')),
        verified_count=Count('id', filter=Q(status='verified')),
        rejected_count=Count('id', filter=Q(status='rejected')),
    )
    submissions = PaymentSubmission.objects.select_related('client', 'bill', 'verified_by').all()
    if status_filter in ('pending', 'verified', 'rejected'):
        submissions = submissions.filter(status=status_filter)

    site_lang = request.session.get('site_lang', 'en')
    context = {
        'submissions': submissions,
        'status_filter': status_filter,
        'submission_counts': submission_counts,
        'title': 'ग्राहक यूपीआई भुगतान सत्यापन' if site_lang == 'hi' else 'Customer UPI Payment Submissions',
    }
    return render(request, 'billing/payment_submissions_list.html', context)

@login_required
def payment_info_settings(request):
    site_lang = request.session.get('site_lang', 'en')
    payment_info = PaymentInfo.get_solo()

    if request.method == 'POST':
        form = PaymentInfoForm(request.POST, instance=payment_info, site_lang=site_lang)
        if form.is_valid():
            form.save()
            msg = (
                "बैंक व यूपीआई विवरण सफलतापूर्वक अपडेट कर दिया गया है! खाता संख्या डेटाबेस में एन्क्रिप्टेड रूप में सुरक्षित है।"
                if site_lang == 'hi'
                else "Bank and UPI details updated successfully! Sensitive account number is encrypted and secured at rest."
            )
            messages.success(request, msg)
            return redirect('billing:payment_info_settings')
    else:
        form = PaymentInfoForm(instance=payment_info, site_lang=site_lang)

    test_qr_base64 = None
    if payment_info.upi_id:
        test_qr_base64 = generate_upi_qr_base64(
            upi_id=payment_info.upi_id,
            payee_name=payment_info.account_holder_name or payment_info.newspaper_name,
            amount=Decimal('100.00'),
            bill_number='TEST-QR',
        )

    context = {
        'form': form,
        'payment_info': payment_info,
        'test_qr_base64': test_qr_base64,
        'title': 'बैंक खाता व यूपीआई सेटिंग्स' if site_lang == 'hi' else 'Bank & UPI Settings',
    }
    return render(request, 'billing/payment_info_settings.html', context)

