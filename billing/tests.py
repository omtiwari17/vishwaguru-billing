from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from billing.models import Bill, PaymentInfo, PlacementType, PaymentStatus, EditionChoice, Client as ClientModel
from billing.utils import (
    generate_bill_number,
    generate_upi_qr_base64,
    amount_in_words_bilingual,
)


class VishwaguruBillingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='staff_test',
            password='password123'
        )
        self.client = Client()
        self.client.login(username='staff_test', password='password123')

        self.payment_info = PaymentInfo.get_solo()
        self.payment_info.bank_name = 'State Bank of India'
        self.payment_info.account_number = '123456789012'
        self.payment_info.ifsc_code = 'SBIN0001234'
        self.payment_info.upi_id = 'vishwaguru@sbi'
        self.payment_info.save()

    def test_bill_number_generator(self):
        """Test sequential bill numbering VG-YYYY-NNNN"""
        num1 = generate_bill_number()
        self.assertTrue(num1.startswith('VG-2026-'))
        self.assertEqual(num1.split('-')[-1], '0001')

        # Create bill with this number
        b1 = Bill.objects.create(
            bill_number=num1,
            client_name='Test Client 1',
            client_phone='9876543210',
            placement_type=PlacementType.FRONT_FULL,
            base_amount=Decimal('5000.00'),
            discount_amount=Decimal('500.00'),
            created_by=self.user
        )
        self.assertEqual(b1.total_amount, Decimal('4500.00'))

        # Next bill number should increment
        num2 = generate_bill_number()
        self.assertEqual(num2.split('-')[-1], '0002')

    def test_amount_in_words_bilingual(self):
        """Test Hindi and English currency words conversion"""
        words = amount_in_words_bilingual(Decimal('5420.50'))
        self.assertIn('पाँच हज़ार चार सौ बीस रुपये पचास पैसे मात्र', words['hindi'])
        self.assertIn('Five Thousand Four Hundred And Twenty', words['english'])
        self.assertIn('Paise Only', words['english'])

    def test_upi_qr_code_generation(self):
        """Test generation of base64 PNG QR code"""
        qr_b64 = generate_upi_qr_base64(
            upi_id='vishwaguru@sbi',
            payee_name='Vishwaguru',
            amount=Decimal('4500.00'),
            bill_number='VG-2026-0001'
        )
        self.assertIsNotNone(qr_b64)
        self.assertTrue(qr_b64.startswith('data:image/png;base64,'))

    def test_whatsapp_share_url(self):
        """Test 1-click WhatsApp URL format"""
        bill = Bill.objects.create(
            bill_number='VG-2026-0001',
            client_name='Sharma Traders',
            client_phone='9893012345',
            placement_type=PlacementType.FRONT_HALF,
            edition_name=EditionChoice.INDORE,
            base_amount=Decimal('3000.00'),
            discount_amount=Decimal('0.00'),
            epaper_link='https://example.com/epaper/post123',
            created_by=self.user
        )
        url = bill.whatsapp_share_url
        self.assertTrue(url.startswith('https://wa.me/919893012345?text='))
        self.assertIn('VG-2026-0001', url)

    def test_bill_create_view(self):
        """Test creating a bill through HTTP POST"""
        url = reverse('billing:bill_create')
        data = {
            'bill_language': 'en',
            'client_name': 'Agrawal Sweets',
            'client_phone': '9826011223',
            'client_address': 'Sarafa Bazaar, Indore',
            'client_gstin': '23ABCDE1234F1Z5',
            'placement_type': PlacementType.INSIDE_HALF,
            'custom_size_text': '',
            'ad_title': 'Diwali Greeting Ad',
            'edition_date': '2026-09-23',
            'edition_name': EditionChoice.INDORE,
            'page_number': 'Page 3',
            'epaper_link': 'https://example.com/ad',
            'base_amount': '2500.00',
            'discount_amount': '200.00',
            'payment_status': PaymentStatus.PARTIAL,
            'amount_paid': '1000.00',
            'payment_method': 'UPI',
            'payment_note': 'GPay Ref 12345',
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        bill = Bill.objects.filter(client_name='Agrawal Sweets').first()
        self.assertIsNotNone(bill)
        self.assertEqual(bill.total_amount, Decimal('2300.00'))
        self.assertEqual(bill.balance_amount, Decimal('1300.00'))
        self.assertEqual(bill.bill_language, 'en')

    def test_bill_search_view(self):
        """Test searching bills by query text"""
        Bill.objects.create(
            bill_number='VG-2026-0099',
            client_name='Unique Search Name',
            client_phone='9999999999',
            placement_type=PlacementType.EAR_PANEL,
            base_amount=Decimal('1000.00'),
            discount_amount=Decimal('0.00'),
            created_by=self.user
        )
        response = self.client.get(reverse('billing:bill_search'), {'q': 'Unique Search'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'VG-2026-0099')
        self.assertContains(response, 'Unique Search Name')

    def test_language_switch_view(self):
        """Test toggling language between en and hi"""
        res = self.client.get(reverse('billing:set_language', args=['hi']), follow=True)
        self.assertEqual(self.client.session.get('site_lang'), 'hi')
        self.assertEqual(res.status_code, 200)

        res2 = self.client.get(reverse('billing:set_language', args=['en']), follow=True)
        self.assertEqual(self.client.session.get('site_lang'), 'en')
        self.assertEqual(res2.status_code, 200)

    def test_bill_form_language_placeholders_and_choices(self):
        """Test that English mode contains English placeholders/choices and Hindi mode contains Hindi"""
        from billing.forms import BillForm

        # English Form
        form_en = BillForm(site_lang='en')
        self.assertEqual(form_en.fields['client_name'].widget.attrs['placeholder'], 'e.g. Shri Ram Traders')
        self.assertEqual(form_en.fields['client_phone'].widget.attrs['placeholder'], '10-digit mobile number (Optional)')
        self.assertFalse(form_en.fields['client_phone'].required)
        placement_labels_en = [label for _, label in form_en.fields['placement_type'].choices]
        self.assertIn('Front Page — Full Page', placement_labels_en)
        edition_labels_en = [label for _, label in form_en.fields['edition_name'].choices]
        self.assertIn('Indore', edition_labels_en)
        status_labels_en = [label for _, label in form_en.fields['payment_status'].choices]
        self.assertIn('Unpaid', status_labels_en)

        # Hindi Form
        form_hi = BillForm(site_lang='hi')
        self.assertEqual(form_hi.fields['client_name'].widget.attrs['placeholder'], 'उदा. श्री राम ट्रेडर्स')
        self.assertEqual(form_hi.fields['client_phone'].widget.attrs['placeholder'], '10 अंकों का मोबाइल नंबर (वैकल्पिक)')
        self.assertFalse(form_hi.fields['client_phone'].required)
        placement_labels_hi = [label for _, label in form_hi.fields['placement_type'].choices]
        self.assertIn('मुख्य पृष्ठ - पूरा पेज', placement_labels_hi)
        edition_labels_hi = [label for _, label in form_hi.fields['edition_name'].choices]
        self.assertIn('इंदौर', edition_labels_hi)
        status_labels_hi = [label for _, label in form_hi.fields['payment_status'].choices]
        self.assertIn('अदत्त', status_labels_hi)

    def test_bill_create_without_phone(self):
        """Test creating a bill without entering a client phone number"""
        url = reverse('billing:bill_create')
        data = {
            'bill_language': 'en',
            'client_name': 'Walk-in Client',
            'client_phone': '',
            'client_address': '',
            'client_gstin': '',
            'placement_type': PlacementType.INSIDE_QUARTER,
            'custom_size_text': '',
            'ad_title': 'Classified Ad',
            'edition_date': '2026-09-23',
            'edition_name': EditionChoice.INDORE,
            'page_number': 'Page 5',
            'epaper_link': '',
            'base_amount': '1500.00',
            'discount_amount': '0.00',
            'payment_status': PaymentStatus.PAID,
            'amount_paid': '1500.00',
            'payment_method': 'Cash',
            'payment_note': '',
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        bill = Bill.objects.filter(client_name='Walk-in Client').first()
        self.assertIsNotNone(bill)
        self.assertEqual(bill.client_phone, '')
        self.assertTrue(bill.whatsapp_share_url.startswith('https://wa.me/?text='))

    def test_client_memory_and_auto_sync(self):
        """Test that creating a bill automatically remembers/updates Client directory"""
        url = reverse('billing:bill_create')
        data = {
            'bill_language': 'en',
            'client_name': 'Kothari Jewellers',
            'client_phone': '9826199999',
            'client_address': 'MG Road, Indore',
            'client_gstin': '23ABCDE9999Z1',
            'placement_type': PlacementType.FRONT_FULL,
            'custom_size_text': '',
            'ad_title': 'Gold Scheme Launch',
            'edition_date': '2026-09-24',
            'edition_name': EditionChoice.INDORE,
            'page_number': 'Page 1',
            'epaper_link': '',
            'base_amount': '5000.00',
            'discount_amount': '0.00',
            'previous_due': '0.00',
            'payment_status': PaymentStatus.PAID,
            'amount_paid': '5000.00',
            'payment_method': 'Cash',
            'payment_note': '',
        }
        res = self.client.post(url, data, follow=True)
        self.assertEqual(res.status_code, 200)

        # Verify Client record was created
        client_rec = ClientModel.objects.filter(name='Kothari Jewellers').first()
        self.assertIsNotNone(client_rec)
        self.assertEqual(client_rec.phone, '9826199999')
        self.assertEqual(client_rec.address, 'MG Road, Indore')
        self.assertEqual(client_rec.gstin, '23ABCDE9999Z1')

    def test_client_search_api_and_pending_due(self):
        """Test client search API endpoint returns matching clients and unpaid pending balance"""
        # Create client directory entry
        ClientModel.objects.create(
            name='Malwa Automotives',
            phone='9893055555',
            address='Vijay Nagar, Indore',
            gstin='23XYZ1234'
        )

        # Create an unpaid bill for this client
        Bill.objects.create(
            bill_number='VG-2026-0101',
            client_name='Malwa Automotives',
            client_phone='9893055555',
            placement_type=PlacementType.FRONT_HALF,
            base_amount=Decimal('4000.00'),
            discount_amount=Decimal('500.00'),
            previous_due=Decimal('0.00'),
            payment_status=PaymentStatus.UNPAID,
            amount_paid=Decimal('0.00'),
            created_by=self.user
        )

        # Query API for 'Malwa'
        url = reverse('billing:client_search_api') + '?q=Malwa'
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        json_data = res.json()
        self.assertIn('clients', json_data)
        self.assertEqual(len(json_data['clients']), 1)
        client_item = json_data['clients'][0]
        self.assertEqual(client_item['name'], 'Malwa Automotives')
        self.assertEqual(client_item['phone'], '9893055555')
        # Total due for 4000 - 500 = 3500 unpaid
        self.assertEqual(client_item['pending_due'], 3500.0)

    def test_bill_with_previous_due(self):
        """Test creating a bill with previous due adds to total amount and renders properly"""
        url = reverse('billing:bill_create')
        data = {
            'bill_language': 'en',
            'client_name': 'Apex Coaching',
            'client_phone': '9893044444',
            'client_address': 'Bhawarkua, Indore',
            'client_gstin': '',
            'placement_type': PlacementType.INSIDE_HALF,
            'custom_size_text': '',
            'ad_title': 'Admissions Open 2026',
            'edition_date': '2026-09-24',
            'edition_name': EditionChoice.INDORE,
            'page_number': 'Page 4',
            'epaper_link': '',
            'base_amount': '3000.00',
            'discount_amount': '200.00',
            'previous_due': '1500.00',
            'payment_status': PaymentStatus.PARTIAL,
            'amount_paid': '2000.00',
            'payment_method': 'UPI',
            'payment_note': 'Paytm 9988',
        }
        res = self.client.post(url, data, follow=True)
        self.assertEqual(res.status_code, 200)

        bill = Bill.objects.filter(client_name='Apex Coaching').first()
        self.assertIsNotNone(bill)
        # (3000 - 200) + 1500 = 4300
        self.assertEqual(bill.total_amount, Decimal('4300.00'))
        # Balance = 4300 - 2000 = 2300
        self.assertEqual(bill.balance_amount, Decimal('2300.00'))
        self.assertEqual(bill.previous_due, Decimal('1500.00'))

        # Check detail page contains Previous Due
        detail_res = self.client.get(reverse('billing:bill_detail', args=[bill.pk]))
        self.assertEqual(detail_res.status_code, 200)
        self.assertContains(detail_res, '1500.00')

        # Check PDF view contains Previous Due
        pdf_res = self.client.get(reverse('billing:bill_pdf', args=[bill.pk]))
        self.assertEqual(pdf_res.status_code, 200)
        self.assertContains(pdf_res, '1500.00')


