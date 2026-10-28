def language_context(request):
    """
    Provides current UI language ('en' for English default, or 'hi' for Hindi)
    and global pending UPI submissions count for staff.
    """
    pending_count = 0
    if getattr(request, 'user', None) and request.user.is_authenticated:
        try:
            from billing.models import PaymentSubmission
            pending_count = PaymentSubmission.objects.filter(status='pending').count()
        except Exception:
            pending_count = 0

    return {
        'site_lang': request.session.get('site_lang', 'en'),
        'pending_submissions_count': pending_count,
    }
