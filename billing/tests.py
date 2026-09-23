from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from billing.models import Bill, PaymentInfo, PlacementType, PaymentStatus, EditionChoice
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
