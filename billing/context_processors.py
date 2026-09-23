def language_context(request):
    """
    Provides current UI language ('en' for English default, or 'hi' for Hindi).
    """
    return {
        'site_lang': request.session.get('site_lang', 'en'),
    }
