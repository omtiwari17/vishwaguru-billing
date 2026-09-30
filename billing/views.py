from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import render_to_string
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from django.utils import timezone

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
    BillForm,
    BillPaymentUpdateForm,
    CustomerPaymentSubmissionForm,
)
from billing.utils import (
    generate_bill_number,
    generate_upi_qr_base64,
    get_upi_intent_url,
    amount_in_words_bilingual,
)


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
        client_obj = Client.objects.filter(name__iexact=bill.client_name.strip()).first()
        if client_obj and not bill.client:
            bill.client = client_obj
            bill.save(update_fields=['client'])

    if client_obj:
        pending_submissions = client_obj.payment_submissions.filter(status='pending')

    site_lang = request.session.get('site_lang', 'en')
    context = {
        'bill': bill,
        'client': client_obj,
        'payment_info': payment_info,
        'amount_words': amount_words,
        'qr_code_base64': qr_code_base64,
        'payment_form': BillPaymentUpdateForm(instance=bill, site_lang=site_lang),
        'pending_submissions': pending_submissions,
        'portal_url': client_obj.get_portal_url(request) if client_obj else "",
        'whatsapp_portal_share_url': client_obj.get_whatsapp_portal_share_url(request) if client_obj else "",
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
    pdf_lang = request.GET.get('lang', getattr(bill, 'bill_language', 'en') or 'en')

    context = {
        'bill': bill,
        'payment_info': payment_info,
        'amount_words': amount_words,
        'qr_code_base64': qr_code_base64,
        'pdf_lang': pdf_lang,
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

        return response
    except Exception as e:
        # Fallback for environments where WeasyPrint native C-libraries are missing
        # Renders the HTML print view directly so user can browser-print to PDF
        messages.warning(
            request,
            f"PDF generator notice: {str(e)}. Rendering high-resolution print view instead."
        )
        return render(request, 'billing/bill_pdf.html', context)


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
    Quick endpoint to update payment status and received amount.
    """
    site_lang = request.session.get('site_lang', 'en')
    bill = get_object_or_404(Bill, pk=pk)
    if request.method == 'POST':
        form = BillPaymentUpdateForm(request.POST, instance=bill, site_lang=site_lang)
        if form.is_valid():
            form.save()
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
        else:
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

    pdf_lang = request.GET.get('lang', getattr(bill, 'bill_language', 'en') or 'en')

    context = {
        'bill': bill,
        'payment_info': payment_info,
        'amount_words': amount_words,
        'qr_code_base64': qr_code_base64,
        'pdf_lang': pdf_lang,
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
        return response
    except Exception as e:
        return render(request, 'billing/bill_pdf.html', context)


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

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/bills/search/'
    return redirect(next_url)


@login_required
def payment_submissions_list(request):
    """
    Staff view to review all customer payment submissions.
    """
    status_filter = request.GET.get('status', 'pending')
    submissions = PaymentSubmission.objects.select_related('client', 'bill', 'verified_by').all()
    if status_filter in ('pending', 'verified', 'rejected'):
        submissions = submissions.filter(status=status_filter)

    site_lang = request.session.get('site_lang', 'en')
    context = {
        'submissions': submissions,
        'status_filter': status_filter,
        'title': 'ग्राहक यूपीआई भुगतान सत्यापन' if site_lang == 'hi' else 'Customer UPI Payment Submissions',
    }
    return render(request, 'billing/payment_submissions_list.html', context)

