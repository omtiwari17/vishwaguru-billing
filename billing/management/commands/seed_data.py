from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from billing.models import Bill, PaymentInfo, PlacementType, EditionChoice, PaymentStatus, PaymentMethod
from billing.utils import generate_bill_number


class Command(BaseCommand):
    help = 'Seeds initial staff user, payment info, and sample bills for testing'

    def handle(self, *args, **options):
        # 1. Ensure admin staff user exists
        admin_user, created = User.objects.get_or_create(username='admin')
        if created:
            admin_user.set_password('admin123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created staff user: admin (password: admin123)"))
        else:
            self.stdout.write("User 'admin' already exists.")

        # 2. Setup PaymentInfo
        payment_info = PaymentInfo.get_solo()
        payment_info.newspaper_name = 'विश्वगुरु'
        payment_info.tagline = 'दैनिक समाचार पत्र (Daily Hindi Newspaper)'
        payment_info.registration_no = 'RNI Reg. No. MP-HIN/2018/12345'
        payment_info.bank_name = 'State Bank of India'
        payment_info.account_number = '389104829104'
        payment_info.ifsc_code = 'SBIN0001234'
        payment_info.account_holder_name = 'Vishwaguru Newspaper'
        payment_info.upi_id = 'vishwaguru@sbi'
        payment_info.phone_number = '+91 98260 12345'
        payment_info.email = 'vishwagurunews@gmail.com'
        payment_info.office_address = 'प्रेस परिसर, एम.जी. रोड, इंदौर (म.प्र.) - 452001'
        payment_info.save()
        self.stdout.write(self.style.SUCCESS("Updated default PaymentInfo for Vishwaguru."))

        # 3. Create Sample Bills if none exist
        if not Bill.objects.exists():
            bill1 = Bill.objects.create(
                bill_number=generate_bill_number(),
                client_name='श्री राम ज्वेलर्स (Shri Ram Jewellers)',
                client_phone='9826011111',
                client_address='सराफा बाजार, इंदौर (म.प्र.)',
                client_gstin='23AABCU9603R1ZM',
                placement_type=PlacementType.FRONT_HALF,
                custom_size_text='16x12 सेमी',
                ad_title='धनतेरस व दीपावली महोत्सव महासेल',
                edition_date=timezone.now().date(),
                edition_name=EditionChoice.INDORE,
                page_number='Page 1',
                epaper_link='https://vishwagurunews.blogspot.com/2026/09/edition-today.html',
                base_amount=Decimal('8000.00'),
                discount_amount=Decimal('500.00'),
                payment_status=PaymentStatus.PAID,
                amount_paid=Decimal('7500.00'),
                payment_method=PaymentMethod.UPI,
                payment_note='PhonePe UTR: 238910489102',
                created_by=admin_user,
            )

            bill2 = Bill.objects.create(
                bill_number=generate_bill_number(),
                client_name='पटेल ऑटोमोबाइल्स (Patel Automobiles)',
                client_phone='9893022222',
                client_address='एबी रोड, भंवरकुआं, इंदौर',
                client_gstin='',
                placement_type=PlacementType.INSIDE_QUARTER,
                custom_size_text='',
                ad_title='नवीन इलेक्ट्रिक स्कूटर लॉन्चिंग',
                edition_date=timezone.now().date(),
                edition_name=EditionChoice.INDORE,
                page_number='Page 4',
                epaper_link='https://vishwagurunews.blogspot.com/2026/09/edition-today.html',
                base_amount=Decimal('3500.00'),
                discount_amount=Decimal('0.00'),
                payment_status=PaymentStatus.UNPAID,
                amount_paid=Decimal('0.00'),
                payment_method=PaymentMethod.CASH,
                payment_note='',
                created_by=admin_user,
            )

            self.stdout.write(self.style.SUCCESS(f"Created sample bills: {bill1.bill_number}, {bill2.bill_number}"))
        else:
            self.stdout.write("Bills already exist, skipping sample creation.")
