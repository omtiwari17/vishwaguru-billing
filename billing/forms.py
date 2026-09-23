from django import forms
from billing.models import Bill, PaymentStatus, PaymentMethod, PlacementType, EditionChoice


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
                'placeholder': 'उदा. श्री राम ट्रेडर्स / Shri Ram Traders',
                'required': True,
            }),
            'client_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '10 अंकों का मोबाइल नंबर (WhatsApp)',
                'required': True,
            }),
            'client_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'दुकान / कार्यालय का पता, शहर',
            }),
            'client_gstin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'वैकल्पिक पैन / जीएसटी नंबर',
            }),
            'placement_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_placement_type',
            }),
            'custom_size_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'उदा. 12 सेमी x 8 सेमी (यदि अन्य आकार चुना हो)',
                'id': 'id_custom_size_text',
            }),
            'ad_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'उदा. दीपावली शुभकामना संदेश / शोरूम उद्घाटन',
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
                'placeholder': 'उदा. Page 1, Page 3',
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
                'placeholder': 'उदा. UTR No. 238910482910 या चेक नं 482910',
            }),
        }

    def clean_client_phone(self):
        phone = self.cleaned_data.get('client_phone', '').strip()
        digits = ''.join(c for c in phone if c.isdigit())
        if len(digits) < 10:
            raise forms.ValidationError('कृपया वैध 10 अंकों का मोबाइल नंबर दर्ज करें। (Please enter valid 10-digit phone number)')
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
            'payment_note': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'लेनदेन संदर्भ / UTR / Cheque No.'}),
        }
