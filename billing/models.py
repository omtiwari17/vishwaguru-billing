from decimal import Decimal
import urllib.parse
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class PlacementType(models.TextChoices):
    FRONT_FULL = 'Front Page Full', 'Front Page — Full Page'
    FRONT_HALF = 'Front Page Half', 'Front Page — Half Page'
    FRONT_QUARTER = 'Front Page Quarter', 'Front Page — Quarter (1/4)'
    INSIDE_FULL = 'Inside Page Full', 'Inside Page — Full Page'
    INSIDE_HALF = 'Inside Page Half', 'Inside Page — Half Page'
    INSIDE_QUARTER = 'Inside Page Quarter', 'Inside Page — Quarter (1/4)'
    BACK_FULL = 'Back Page Full', 'Back Page — Full Page'
    BACK_HALF = 'Back Page Half', 'Back Page — Half Page'
    BACK_QUARTER = 'Back Page Quarter', 'Back Page — Quarter (1/4)'
    EAR_PANEL = 'Ear Panel', 'Ear Panel (Top Header)'
    CUSTOM = 'Custom Size', 'Custom Size / Dimensions'


class EditionChoice(models.TextChoices):
    INDORE = 'Indore', 'Indore'
    BHOPAL = 'Bhopal', 'Bhopal'
    UJJAIN = 'Ujjain', 'Ujjain'
    GWALIOR = 'Gwalior', 'Gwalior'
    JABALPUR = 'Jabalpur', 'Jabalpur'
    STATE = 'State Combined', 'All Editions (State Combined)'
    OTHER = 'Other', 'Other'


class PaymentStatus(models.TextChoices):
    UNPAID = 'Unpaid', 'Unpaid'
    PAID = 'Paid', 'Paid'
    PARTIAL = 'Partial', 'Partial'


class PaymentMethod(models.TextChoices):
    CASH = 'Cash', 'Cash'
    UPI = 'UPI', 'UPI / QR Code'
    BANK_TRANSFER = 'Bank Transfer', 'Bank Transfer / NEFT'
    CHEQUE = 'Cheque', 'Cheque'


class BillLanguage(models.TextChoices):
    ENGLISH = 'en', 'English'
    HINDI = 'hi', 'Hindi'
    BILINGUAL = 'bi', 'Bilingual (Hindi + English)'


# Language-specific choice mappings
PLACEMENT_CHOICES_HI = [
    ('Front Page Full', 'मुख्य पृष्ठ - पूरा पेज'),
    ('Front Page Half', 'मुख्य पृष्ठ - आधा पेज'),
    ('Front Page Quarter', 'मुख्य पृष्ठ - चौथाई'),
    ('Inside Page Full', 'अंदर का पृष्ठ - पूरा पेज'),
    ('Inside Page Half', 'अंदर का पृष्ठ - आधा पेज'),
    ('Inside Page Quarter', 'अंदर का पृष्ठ - चौथाई'),
    ('Back Page Full', 'अंतिम पृष्ठ - पूरा पेज'),
    ('Back Page Half', 'अंतिम पृष्ठ - आधा पेज'),
    ('Back Page Quarter', 'अंतिम पृष्ठ - चौथाई'),
    ('Ear Panel', 'शीर्ष विज्ञापन (ईयर पैनल)'),
    ('Custom Size', 'अन्य विशिष्ट आकार'),
]

PLACEMENT_CHOICES_BI = [
    ('Front Page Full', 'मुख्य पृष्ठ - पूरा पेज (Front Page Full)'),
    ('Front Page Half', 'मुख्य पृष्ठ - आधा पेज (Front Page Half)'),
    ('Front Page Quarter', 'मुख्य पृष्ठ - चौथाई (Front Quarter)'),
    ('Inside Page Full', 'अंदर का पृष्ठ - पूरा पेज (Inside Page Full)'),
    ('Inside Page Half', 'अंदर का पृष्ठ - आधा पेज (Inside Page Half)'),
    ('Inside Page Quarter', 'अंदर का पृष्ठ - चौथाई (Inside Quarter)'),
    ('Back Page Full', 'अंतिम पृष्ठ - पूरा पेज (Back Page Full)'),
    ('Back Page Half', 'अंतिम पृष्ठ - आधा पेज (Back Page Half)'),
    ('Back Page Quarter', 'अंतिम पृष्ठ - चौथाई (Back Quarter)'),
    ('Ear Panel', 'शीर्ष विज्ञापन - ईयर पैनल (Ear Panel)'),
    ('Custom Size', 'अन्य आकार (Custom Size)'),
]

EDITION_CHOICES_HI = [
    ('Indore', 'इंदौर'),
    ('Bhopal', 'भोपाल'),
    ('Ujjain', 'उज्जैन'),
    ('Gwalior', 'ग्वालियर'),
    ('Jabalpur', 'जबलपुर'),
    ('State Combined', 'समस्त संस्करण'),
    ('Other', 'अन्य'),
]

EDITION_CHOICES_BI = [
    ('Indore', 'इंदौर (Indore)'),
    ('Bhopal', 'भोपाल (Bhopal)'),
    ('Ujjain', 'उज्जैन (Ujjain)'),
    ('Gwalior', 'ग्वालियर (Gwalior)'),
    ('Jabalpur', 'जबलपुर (Jabalpur)'),
    ('State Combined', 'समस्त संस्करण (All Editions)'),
    ('Other', 'अन्य (Other)'),
]

PAYMENT_STATUS_CHOICES_HI = [
    ('Unpaid', 'अदत्त'),
    ('Paid', 'पूर्ण भुगतान'),
    ('Partial', 'आंशिक भुगतान'),
]

PAYMENT_METHOD_CHOICES_HI = [
    ('Cash', 'नकद'),
    ('UPI', 'यूपीआई (UPI / QR Code)'),
    ('Bank Transfer', 'बैंक ट्रांसफर (NEFT/RTGS)'),
    ('Cheque', 'चेक'),
]

BILL_LANG_CHOICES_HI = [
    ('en', 'अंग्रेजी (English)'),
    ('hi', 'हिंदी (Hindi)'),
    ('bi', 'द्विभाषी (हिंदी + English)'),
]


class PaymentInfo(models.Model):
    """
    Singleton configuration model storing newspaper payment-receiving details
    and letterhead masthead info.
    """
    newspaper_name = models.CharField(
        max_length=150,
        default='विश्वगुरु (Vishwaguru)',
        verbose_name='समाचार पत्र का नाम / Newspaper Name'
    )
    tagline = models.CharField(
        max_length=255,
        default='दैनिक समाचार पत्र / Daily Newspaper',
        verbose_name='टैगलाइन / Tagline'
    )
    registration_no = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='पंजीकरण संख्या / RNI Reg. No.'
    )
    bank_name = models.CharField(
        max_length=150,
        default='State Bank of India',
        verbose_name='बैंक का नाम / Bank Name'
    )
    account_number = models.CharField(
        max_length=50,
        default='',
        verbose_name='खाता संख्या / Account Number'
    )
    ifsc_code = models.CharField(
        max_length=30,
        default='',
        verbose_name='आईएफएससी कोड / IFSC Code'
    )
    account_holder_name = models.CharField(
        max_length=150,
        default='Vishwaguru',
        verbose_name='खाताधारक का नाम / Account Holder Name'
    )
    upi_id = models.CharField(
        max_length=100,
        default='',
        verbose_name='यूपीआई आईडी / UPI ID'
    )
    phone_number = models.CharField(
        max_length=50,
        default='',
        verbose_name='संपर्क फ़ोन / Contact Phone'
    )
    email = models.EmailField(
        blank=True,
        default='',
        verbose_name='ईमेल / Email'
    )
    office_address = models.TextField(
        default='Indore, Madhya Pradesh',
        verbose_name='कार्यालय का पता / Office Address'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'भुगतान व पत्रशीर्ष विवरण (Payment & Letterhead Info)'
        verbose_name_plural = 'भुगतान व पत्रशीर्ष विवरण (Payment & Letterhead Info)'

    def __str__(self):
        return f"{self.newspaper_name} - {self.upi_id or self.account_number}"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj


class Client(models.Model):
    """
    Client / Advertiser master directory for autocomplete, quick recall,
    and outstanding pending balance tracking.
    """
    name = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name='विज्ञापनदाता का नाम / Client Name'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='फ़ोन नंबर / Client Phone'
    )
    address = models.TextField(
        blank=True,
        default='',
        verbose_name='पता व शहर / Client Address'
    )
    gstin = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='पैन / जीएसटी नंबर / GSTIN or PAN'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'ग्राहक / विज्ञापनदाता (Client)'
        verbose_name_plural = 'ग्राहक सूची (Clients)'

    def __str__(self):
        return f"{self.name} ({self.phone or 'No Phone'})"


class Bill(models.Model):
    bill_number = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        verbose_name='बिल क्रमांक / Bill Number'
    )
    bill_language = models.CharField(
        max_length=5,
        choices=BillLanguage.choices,
        default=BillLanguage.ENGLISH,
        verbose_name='बिल की भाषा / Bill Language'
    )
    # Client information
    client_name = models.CharField(
        max_length=200,
        verbose_name='विज्ञापनदाता का नाम / Client Name'
    )
    client_phone = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='फ़ोन नंबर / Client Phone'
    )
    client_address = models.TextField(
        blank=True,
        default='',
        verbose_name='पता व शहर / Client Address'
    )
    client_gstin = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='पैन / जीएसटी नंबर / GSTIN or PAN'
    )

    # Advertisement placement & publication details
    placement_type = models.CharField(
        max_length=50,
        choices=PlacementType.choices,
        default=PlacementType.FRONT_FULL,
        verbose_name='विज्ञापन स्थान व आकार / Placement Preset'
    )
    custom_size_text = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='विशिष्ट आकार / Custom Size (उदा. 8x12 cm)'
    )
    ad_title = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='विज्ञापन शीर्षक / Ad Title or Description'
    )
    edition_date = models.DateField(
        default=timezone.now,
        verbose_name='प्रकाशन दिनांक / Edition Date'
    )
    edition_name = models.CharField(
        max_length=50,
        choices=EditionChoice.choices,
        default=EditionChoice.INDORE,
        verbose_name='संस्करण / Edition Name'
    )
    epaper_link = models.URLField(
        blank=True,
        default='',
        verbose_name='ई-पेपर लिंक / Epaper Verification URL'
    )
    page_number = models.CharField(
        max_length=30,
        blank=True,
        default='Page 1',
        verbose_name='पृष्ठ संख्या / Page Number'
    )

    # Financial breakdown
    base_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='मूल राशि / Base Amount (₹)'
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='छूट / Discount (₹)'
    )
    previous_due = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='पुराना बकाया / Previous Due (₹)'
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='कुल देय राशि / Net Payable Amount (₹)'
    )

    # Payment tracking
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
        verbose_name='भुगतान स्थिति / Payment Status'
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='प्राप्त राशि / Amount Paid (₹)'
    )
    payment_method = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
        default=PaymentMethod.UPI,
        verbose_name='भुगतान माध्यम / Payment Method'
    )
    payment_note = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='भुगतान संदर्भ / UTR or Cheque Note'
    )

    # Audit tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bills',
        verbose_name='बिल निर्माता / Created By'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='निर्माण समय / Created At'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='संशोधन समय / Updated At'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'विज्ञापन बिल (Bill)'
        verbose_name_plural = 'विज्ञापन बिल (Bills)'

    def __str__(self):
        return f"{self.bill_number} - {self.client_name} (₹{self.total_amount})"

    def save(self, *args, **kwargs):
        # Enforce server-side calculation: (Base - Discount) + Previous Due
        self.base_amount = Decimal(str(self.base_amount or '0.00'))
        self.discount_amount = Decimal(str(self.discount_amount or '0.00'))
        self.previous_due = Decimal(str(self.previous_due or '0.00'))
        net_ad = self.base_amount - self.discount_amount
        calculated_total = net_ad + self.previous_due
        self.total_amount = max(Decimal('0.00'), calculated_total)
        super().save(*args, **kwargs)

    @property
    def current_ad_total(self):
        """Current ad charges after discount, excluding previous due."""
        return max(Decimal('0.00'), (self.base_amount or Decimal('0.00')) - (self.discount_amount or Decimal('0.00')))

    @property
    def balance_amount(self):
        """Outstanding unpaid balance."""
        return max(Decimal('0.00'), self.total_amount - (self.amount_paid or Decimal('0.00')))

    @property
    def placement_hindi(self):
        return dict(PLACEMENT_CHOICES_HI).get(self.placement_type, self.placement_type)

    @property
    def placement_bilingual(self):
        return dict(PLACEMENT_CHOICES_BI).get(self.placement_type, self.placement_type)

    @property
    def edition_hindi(self):
        return dict(EDITION_CHOICES_HI).get(self.edition_name, self.edition_name)

    @property
    def edition_bilingual(self):
        return dict(EDITION_CHOICES_BI).get(self.edition_name, self.edition_name)

    @property
    def payment_status_hindi(self):
        return dict(PAYMENT_STATUS_CHOICES_HI).get(self.payment_status, self.payment_status)

    @property
    def payment_method_hindi(self):
        return dict(PAYMENT_METHOD_CHOICES_HI).get(self.payment_method, self.payment_method)

    @property
    def bill_language_hindi(self):
        return dict(BILL_LANG_CHOICES_HI).get(self.bill_language, self.bill_language)

    @property
    def whatsapp_share_url(self):
        """
        Generate a pre-filled direct WhatsApp message URL in English or Hindi.
        """
        clean_phone = ''.join(c for c in (self.client_phone or '') if c.isdigit())
        if len(clean_phone) == 10:
            clean_phone = '91' + clean_phone

        if self.bill_language == 'en':
            lines = [
                f"Dear {self.client_name},",
                f"Greetings from *Vishwaguru Newspaper*.",
                f"Here are your advertisement bill details:",
                f"",
                f"• *Invoice No:* {self.bill_number}",
                f"• *Edition Date:* {self.edition_date.strftime('%d/%m/%Y')}",
                f"• *Edition:* {self.get_edition_name_display()}",
                f"• *Placement:* {self.get_placement_type_display()}",
            ]
            if self.custom_size_text:
                lines.append(f"• *Dimensions:* {self.custom_size_text}")
            if self.page_number:
                lines.append(f"• *Page No:* {self.page_number}")
            lines.extend([
                f"• *Total Amount:* Rs. {self.total_amount:,.2f}",
                f"• *Payment Status:* {self.get_payment_status_display()}",
            ])
            if self.epaper_link:
                lines.append(f"• *Epaper Verification:* {self.epaper_link}")
            lines.extend([
                "",
                "Please review the invoice and complete payment.",
                "Thank you,",
                "*Vishwaguru Newspaper Management*",
            ])
        else:
            lines = [
                f"सादर नमस्ते {self.client_name} जी,",
                f"*विश्वगुरु समाचार पत्र* में आपके विज्ञापन का बिल विवरण निम्न अनुसार है:",
                f"",
                f"• *बिल क्रमांक:* {self.bill_number}",
                f"• *प्रकाशन दिनांक:* {self.edition_date.strftime('%d/%m/%Y')}",
                f"• *संस्करण:* {self.edition_hindi}",
                f"• *स्थान व आकार:* {self.placement_hindi}",
            ]
            if self.custom_size_text:
                lines.append(f"• *माप:* {self.custom_size_text}")
            if self.page_number:
                lines.append(f"• *पृष्ठ क्रमांक:* {self.page_number}")
            lines.extend([
                f"• *कुल देय राशि:* ₹{self.total_amount:,.2f}",
                f"• *भुगतान स्थिति:* {self.payment_status_hindi}",
            ])
            if self.epaper_link:
                lines.append(f"• *ई-पेपर लिंक:* {self.epaper_link}")
            lines.extend([
                "",
                "कृपया बिल का अवलोकन कर भुगतान सुनिश्चित करें।",
                "धन्यवाद,",
                "*विश्वगुरु समाचार पत्र प्रबंधन*",
            ])

        msg = "\n".join(lines)
        encoded_msg = urllib.parse.quote(msg)
        return f"https://wa.me/{clean_phone}?text={encoded_msg}"
