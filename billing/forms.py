from django import forms
from django.utils import timezone
from billing.models import (
    Bill,
    PaymentStatus,
    PaymentMethod,
    PlacementType,
    EditionChoice,
    BillLanguage,
    PLACEMENT_CHOICES_HI,
    EDITION_CHOICES_HI,
    PAYMENT_STATUS_CHOICES_HI,
    PAYMENT_METHOD_CHOICES_HI,
    BILL_LANG_CHOICES_HI,
)


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = [
            'bill_language',
            'client_name',
            'client_phone',
            'client_address',
            'client_gstin',
            'placement_type',
            'custom_size_text',
            'ad_title',
            'edition_date',
            'edition_name',
            'page_number',
            'epaper_link',
            'base_amount',
            'discount_amount',
            'previous_due',
            'payment_status',
            'amount_paid',
            'payment_method',
            'payment_note',
        ]
        widgets = {
            'bill_language': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_bill_language',
            }),
            'client_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'client_phone': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'client_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
            }),
            'client_gstin': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'placement_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_placement_type',
            }),
            'custom_size_text': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_custom_size_text',
            }),
            'ad_title': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'edition_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'edition_name': forms.Select(attrs={
                'class': 'form-select',
            }),
            'page_number': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'epaper_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://vishwagurunews.blogspot.com/...',
            }),
            'base_amount': forms.NumberInput(attrs={
                'class': 'form-control amount-calc',
                'step': '0.01',
                'min': '0',
                'id': 'id_base_amount',
                'required': True,
            }),
            'discount_amount': forms.NumberInput(attrs={
                'class': 'form-control amount-calc',
                'step': '0.01',
                'min': '0',
                'id': 'id_discount_amount',
            }),
            'previous_due': forms.NumberInput(attrs={
                'class': 'form-control amount-calc',
                'step': '0.01',
                'min': '0',
                'id': 'id_previous_due',
            }),
            'payment_status': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_payment_status',
            }),
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'id': 'id_amount_paid',
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select',
            }),
            'payment_note': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, site_lang='en', **kwargs):
        self.site_lang = site_lang
        super().__init__(*args, **kwargs)
        self.fields['client_phone'].required = False
        self.fields['previous_due'].required = False

        if not self.instance.pk:
            self.fields['edition_date'].initial = timezone.localdate().strftime('%Y-%m-%d')
            self.fields['edition_name'].initial = EditionChoice.INDORE
            self.fields['payment_status'].initial = PaymentStatus.PAID
            self.fields['payment_method'].initial = PaymentMethod.CASH
            self.fields['bill_language'].initial = BillLanguage.ENGLISH if site_lang == 'en' else BillLanguage.HINDI
            self.fields['discount_amount'].initial = '0.00'
            self.fields['previous_due'].initial = '0.00'

        if site_lang == 'hi':
            self.fields['placement_type'].choices = PLACEMENT_CHOICES_HI
            self.fields['edition_name'].choices = EDITION_CHOICES_HI
            self.fields['payment_status'].choices = PAYMENT_STATUS_CHOICES_HI
            self.fields['payment_method'].choices = PAYMENT_METHOD_CHOICES_HI
            self.fields['bill_language'].choices = BILL_LANG_CHOICES_HI

            self.fields['client_name'].widget.attrs['placeholder'] = 'उदा. श्री राम ट्रेडर्स'
            self.fields['client_phone'].widget.attrs['placeholder'] = '10 अंकों का मोबाइल नंबर (वैकल्पिक)'
            self.fields['client_address'].widget.attrs['placeholder'] = 'दुकान / कार्यालय का पता, शहर'
            self.fields['client_gstin'].widget.attrs['placeholder'] = 'वैकल्पिक जीएसटी / पैन नंबर'
            self.fields['custom_size_text'].widget.attrs['placeholder'] = 'उदा. 12 सेमी x 8 सेमी'
            self.fields['previous_due'].widget.attrs['placeholder'] = '0.00 (पुराना बकाया यदि कोई हो)'
            self.fields['ad_title'].widget.attrs['placeholder'] = 'उदा. दीपावली शुभकामना संदेश / शोरूम उद्घाटन'
            self.fields['page_number'].widget.attrs['placeholder'] = 'उदा. पृष्ठ 1, पृष्ठ 3'
            self.fields['payment_note'].widget.attrs['placeholder'] = 'उदा. UTR नं 238910482910 या चेक नं 482910'
        else:
            self.fields['placement_type'].choices = PlacementType.choices
            self.fields['edition_name'].choices = EditionChoice.choices
            self.fields['payment_status'].choices = PaymentStatus.choices
            self.fields['payment_method'].choices = PaymentMethod.choices
            self.fields['bill_language'].choices = BillLanguage.choices

            self.fields['client_name'].widget.attrs['placeholder'] = 'e.g. Shri Ram Traders'
            self.fields['client_phone'].widget.attrs['placeholder'] = '10-digit mobile number (Optional)'
            self.fields['client_address'].widget.attrs['placeholder'] = 'Shop / Office address, City'
            self.fields['client_gstin'].widget.attrs['placeholder'] = 'Optional GSTIN or PAN'
            self.fields['custom_size_text'].widget.attrs['placeholder'] = 'e.g. 12cm x 8cm (if custom size selected)'
            self.fields['previous_due'].widget.attrs['placeholder'] = '0.00 (Optional previous due)'
            self.fields['ad_title'].widget.attrs['placeholder'] = 'e.g. Diwali Greeting Ad / Showroom Inauguration'
            self.fields['page_number'].widget.attrs['placeholder'] = 'e.g. Page 1, Page 3'
            self.fields['payment_note'].widget.attrs['placeholder'] = 'e.g. UTR No. 238910482910 or Cheque No. 482910'

    def clean_client_phone(self):
        phone = self.cleaned_data.get('client_phone', '').strip()
        if not phone:
            return ''
        digits = ''.join(c for c in phone if c.isdigit())
        if len(digits) < 10:
            if getattr(self, 'site_lang', 'en') == 'hi':
                raise forms.ValidationError('कृपया वैध 10 अंकों का मोबाइल नंबर दर्ज करें या खाली छोड़ें।')
            raise forms.ValidationError('Please enter a valid 10-digit mobile phone number or leave blank.')
        return phone


class BillPaymentUpdateForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = [
            'payment_status',
            'amount_paid',
            'payment_method',
            'payment_note',
        ]
        widgets = {
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'payment_note': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, site_lang='en', **kwargs):
        super().__init__(*args, **kwargs)
        if site_lang == 'hi':
            self.fields['payment_status'].choices = PAYMENT_STATUS_CHOICES_HI
            self.fields['payment_method'].choices = PAYMENT_METHOD_CHOICES_HI
            self.fields['payment_note'].widget.attrs['placeholder'] = 'लेनदेन संदर्भ / UTR / चेक नं.'
        else:
            self.fields['payment_status'].choices = PaymentStatus.choices
            self.fields['payment_method'].choices = PaymentMethod.choices
            self.fields['payment_note'].widget.attrs['placeholder'] = 'Transaction Reference / UTR / Cheque No.'
