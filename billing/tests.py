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
        self.assertContains(detail_res, '1,500')

        # Check PDF view contains Previous Due
        pdf_res = self.client.get(reverse('billing:bill_pdf', args=[bill.pk]))
        self.assertEqual(pdf_res.status_code, 200)

    def test_customer_portal_wrong_or_unknown_token_returns_404(self):
        """Test that an unknown or invalid access token returns 404 and leaks zero client data"""
        import uuid
        unknown_token = uuid.uuid4()
        anon_client = Client()
        portal_url = reverse('billing:customer_portal', kwargs={'token': str(unknown_token)})
        response = anon_client.get(portal_url)
        self.assertEqual(response.status_code, 404)
        self.assertNotContains(response, 'Rajesh Electronics', status_code=404)

        # Also verify invalid token on customer payment submission and PDF routes
        submit_url = reverse('billing:customer_payment_submit', kwargs={'token': str(unknown_token)})
        self.assertEqual(anon_client.post(submit_url, {}).status_code, 404)

        pdf_url = reverse('billing:customer_bill_pdf', kwargs={'token': str(unknown_token), 'bill_id': 9999})
        self.assertEqual(anon_client.get(pdf_url).status_code, 404)

    def test_customer_portal_and_upi_intent(self):
        """Test customer portal rendering, outstanding balance calculation, and UPI deep-link generation"""
        client_obj = ClientModel.objects.create(
            name='Rajesh Electronics',
            phone='9893099999',
            address='MG Road, Indore'
        )
        self.assertIsNotNone(client_obj.access_token)

        # Unpaid Bill 1
        b1 = Bill.objects.create(
            bill_number='VG-2026-0091',
            client=client_obj,
            client_name='Rajesh Electronics',
            placement_type=PlacementType.FRONT_HALF,
            base_amount=Decimal('4000.00'),
            discount_amount=Decimal('0.00'),
            payment_status=PaymentStatus.UNPAID,
            amount_paid=Decimal('0.00'),
            created_by=self.user
        )

        # Paid Bill 2
        b2 = Bill.objects.create(
            bill_number='VG-2026-0092',
            client=client_obj,
            client_name='Rajesh Electronics',
            placement_type=PlacementType.INSIDE_HALF,
            base_amount=Decimal('2500.00'),
            discount_amount=Decimal('0.00'),
            payment_status=PaymentStatus.PAID,
            amount_paid=Decimal('2500.00'),
            created_by=self.user
        )

        self.assertEqual(client_obj.total_billed, Decimal('6500.00'))
        self.assertEqual(client_obj.total_paid, Decimal('2500.00'))
        self.assertEqual(client_obj.total_outstanding, Decimal('4000.00'))

        # Access customer portal without staff authentication (unauthenticated client)
        anon_client = Client()
        portal_url = reverse('billing:customer_portal', kwargs={'token': str(client_obj.access_token)})
        response = anon_client.get(portal_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rajesh Electronics')
        self.assertContains(response, '4000.00') # Balance Due
        self.assertContains(response, 'VG-2026-0091') # Unpaid bill
        self.assertContains(response, 'VG-2026-0092') # Paid bill

        # Check short redirect route: /c/<token>/
        short_url = reverse('billing:customer_portal_short', kwargs={'token': str(client_obj.access_token)})
        short_res = anon_client.get(short_url)
        self.assertEqual(short_res.status_code, 302)
        self.assertIn(str(client_obj.access_token), short_res.url)

        # Check customer bill PDF access without staff login
        pdf_url = reverse('billing:customer_bill_pdf', kwargs={'token': str(client_obj.access_token), 'bill_id': b1.id})
        pdf_res = anon_client.get(pdf_url)
        self.assertEqual(pdf_res.status_code, 200)

    def test_customer_payment_submission_and_staff_verification(self):
        """Test customer submitting UTR reference and staff verifying it to clear bill"""
        client_obj = ClientModel.objects.create(
            name='Khandelwal Jewellers',
            phone='9893088888',
        )
        bill = Bill.objects.create(
            bill_number='VG-2026-0095',
            client=client_obj,
            client_name='Khandelwal Jewellers',
            placement_type=PlacementType.FRONT_FULL,
            base_amount=Decimal('8000.00'),
            discount_amount=Decimal('0.00'),
            payment_status=PaymentStatus.UNPAID,
            amount_paid=Decimal('0.00'),
            created_by=self.user
        )

        # 1. Customer submits invalid UTR (non-numeric, wrong length) on public portal
        anon_client = Client()
        submit_url = reverse('billing:customer_payment_submit', kwargs={'token': str(client_obj.access_token)})
        
        # Test non-numeric UTR returns validation error (English via HTMX)
        bad_res_en = anon_client.post(
            f"{submit_url}?lang=en",
            {
                'bill': bill.id,
                'amount': '8000.00',
                'utr_number': 'ABC123456789',
            },
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(bad_res_en.status_code, 200)
        self.assertContains(bad_res_en, "UTR number must be exactly 12 digits (numeric only).")

        # Test non-numeric UTR returns validation error (Hindi via HTMX)
        bad_res_hi = anon_client.post(
            f"{submit_url}?lang=hi",
            {
                'bill': bill.id,
                'amount': '8000.00',
                'utr_number': '12345',  # too short
            },
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(bad_res_hi.status_code, 200)
        self.assertContains(bad_res_hi, "यूटीआर संख्या ठीक 12 अंकों की होनी चाहिए (केवल 0-9)।")

        # Now submit a valid 12-digit numeric UTR
        post_data = {
            'bill': bill.id,
            'amount': '8000.00',
            'utr_number': '429812345678',
            'notes': 'Paid via PhonePe by Ramesh',
        }
        submit_res = anon_client.post(submit_url, post_data, follow=True)
        self.assertEqual(submit_res.status_code, 200)

        # Check submission created in database with status 'pending'
        from billing.models import PaymentSubmission
        submission = PaymentSubmission.objects.filter(utr_number='429812345678').first()
        self.assertIsNotNone(submission)
        self.assertEqual(submission.status, 'pending')
        self.assertEqual(submission.amount, Decimal('8000.00'))

        # 2. Staff views bill_detail and verifies payment submission
        verify_url = reverse('billing:verify_payment_submission', args=[submission.id])
        verify_res = self.client.post(verify_url, {'action': 'verify'}, follow=True)
        self.assertEqual(verify_res.status_code, 200)

        # Verify bill is now marked PAID with UTR recorded
        bill.refresh_from_db()
        submission.refresh_from_db()
        self.assertEqual(submission.status, 'verified')
        self.assertEqual(bill.payment_status, PaymentStatus.PAID)
        self.assertEqual(bill.amount_paid, Decimal('8000.00'))
        self.assertEqual(bill.balance_amount, Decimal('0.00'))
        self.assertIn('429812345678', bill.payment_note)

    def test_dashboard_view_authenticated(self):
        Bill.objects.create(
            bill_number='VG-2026-0099',
            client_name='Test Advertiser Ltd',
            client_phone='9999900000',
            placement_type=PlacementType.FRONT_FULL,
            base_amount=Decimal('10000.00'),
            discount_amount=Decimal('1000.00'),
            payment_status=PaymentStatus.PARTIAL,
            amount_paid=Decimal('4000.00'),
            created_by=self.user
        )

        url = reverse('billing:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Advertiser Ltd')
        self.assertContains(response, 'VG-2026-0099')
        self.assertIn('today_billed', response.context)
        self.assertIn('total_outstanding', response.context)
        self.assertIn('recent_bills', response.context)

    def test_dashboard_view_unauthenticated(self):
        anon_client = Client()
        url = reverse('billing:dashboard')
        response = anon_client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_root_redirects_to_dashboard(self):
        response = self.client.get('/', follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('billing:dashboard'))

    def test_payment_info_encryption_at_rest(self):
        from django.db import connection
        payment_info = PaymentInfo.get_solo()
        payment_info.account_number = '987654321098'
        payment_info.save()

        reloaded = PaymentInfo.objects.get(id=payment_info.id)
        self.assertEqual(reloaded.account_number, '987654321098')
        self.assertTrue(reloaded.masked_account_number.endswith('1098'))

        with connection.cursor() as cursor:
            cursor.execute('SELECT account_number FROM billing_paymentinfo WHERE id = %s', [payment_info.id])
            raw_in_db = cursor.fetchone()[0]
        self.assertTrue(raw_in_db.startswith('enc:'))
        self.assertNotIn('987654321098', raw_in_db)

    def test_payment_info_stdlib_crypto_fallback(self):
        from unittest.mock import patch
        from billing.crypto import encrypt_value, decrypt_value

        with patch('billing.crypto.HAS_CRYPTOGRAPHY', False):
            ciphertext = encrypt_value('555444333222')
            self.assertTrue(ciphertext.startswith('enc:std:'))
            decrypted = decrypt_value(ciphertext)
            self.assertEqual(decrypted, '555444333222')

    def test_payment_info_settings_view(self):
        url = reverse('billing:payment_info_settings')

        get_res = self.client.get(url)
        self.assertEqual(get_res.status_code, 200)
        self.assertContains(get_res, 'vishwaguru@sbi')

        post_data = {
            'newspaper_name': 'विश्वगुरु (Vishwaguru)',
            'tagline': 'दैनिक समाचार पत्र',
            'registration_no': 'RNI-MP-12345',
            'bank_name': 'HDFC Bank',
            'account_holder_name': 'Vishwaguru Publication',
            'account_number': '50100234567890',
            'ifsc_code': 'HDFC0001234',
            'upi_id': 'vishwaguru@hdfc',
            'phone_number': '9893012345',
            'email': 'billing@vishwaguru.com',
            'office_address': 'Indore, MP',
        }
        post_res = self.client.post(url, post_data, follow=True)
        self.assertEqual(post_res.status_code, 200)

        updated_info = PaymentInfo.get_solo()
        self.assertEqual(updated_info.bank_name, 'HDFC Bank')
        self.assertEqual(updated_info.account_number, '50100234567890')
        self.assertEqual(updated_info.ifsc_code, 'HDFC0001234')
        self.assertEqual(updated_info.upi_id, 'vishwaguru@hdfc')

    def test_payment_info_settings_unauthenticated(self):
        anon_client = Client()
        url = reverse('billing:payment_info_settings')
        response = anon_client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_record_payment_validation_amount(self):
        """Test amount validation: amount > 0 and amount <= balance_amount in EN and HI."""
        bill = Bill.objects.create(
            bill_number='VG-2026-0091',
            client_name='Test Advertiser',
            client_phone='9898989898',
            base_amount=Decimal('3500.00'),
            total_amount=Decimal('3500.00'),
            amount_paid=Decimal('0.00'),
            payment_status=PaymentStatus.UNPAID,
            created_by=self.user,
        )
        url = reverse('billing:bill_payment_update', kwargs={'pk': bill.pk})

        # 1. English: Amount <= 0
        res = self.client.post(url, {
            'amount': '0.00',
            'payment_method': 'Cash',
            'reference': '',
            'note': '',
        }, HTTP_HX_REQUEST='true')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Amount must be greater than zero.')

        # 2. English: Amount > balance_amount
        res = self.client.post(url, {
            'amount': '4000.00',
            'payment_method': 'Cash',
            'reference': '',
            'note': '',
        }, HTTP_HX_REQUEST='true')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Amount cannot exceed balance due')

        # 3. Hindi: Amount <= 0 and Amount > balance_amount
        session = self.client.session
        session['site_lang'] = 'hi'
        session.save()

        res_hi_zero = self.client.post(url, {
            'amount': '0.00',
            'payment_method': 'Cash',
            'reference': '',
            'note': '',
        }, HTTP_HX_REQUEST='true')
        self.assertEqual(res_hi_zero.status_code, 200)
        self.assertContains(res_hi_zero, 'राशि शून्य से अधिक होनी चाहिए।')

        res_hi_exceed = self.client.post(url, {
            'amount': '5000.00',
            'payment_method': 'Cash',
            'reference': '',
            'note': '',
        }, HTTP_HX_REQUEST='true')
        self.assertEqual(res_hi_exceed.status_code, 200)
        self.assertContains(res_hi_exceed, 'राशि शेष बकाया')

        # Reset session back to English
        session['site_lang'] = 'en'
        session.save()

    def test_record_payment_validation_upi_reference(self):
        """Test UPI payment mode requires exactly 12 numeric digits in reference."""
        bill = Bill.objects.create(
            bill_number='VG-2026-0092',
            client_name='Test Advertiser 2',
            base_amount=Decimal('2000.00'),
            total_amount=Decimal('2000.00'),
            amount_paid=Decimal('0.00'),
            payment_status=PaymentStatus.UNPAID,
            created_by=self.user,
        )
        url = reverse('billing:bill_payment_update', kwargs={'pk': bill.pk})

        # Missing reference for UPI
        res_empty = self.client.post(url, {
            'amount': '2000.00',
            'payment_method': 'UPI',
            'reference': '',
            'note': '',
        }, HTTP_HX_REQUEST='true')
        self.assertEqual(res_empty.status_code, 200)
        self.assertContains(res_empty, '12-digit UTR is required for UPI payment.')

        # Invalid reference (11 digits or non-digits)
        res_invalid = self.client.post(url, {
            'amount': '2000.00',
            'payment_method': 'UPI',
            'reference': '12345ABC',
            'note': '',
        }, HTTP_HX_REQUEST='true')
        self.assertEqual(res_invalid.status_code, 200)
        self.assertContains(res_invalid, 'UTR must be exactly 12 digits (numeric only).')

    def test_record_payment_success_flow_and_history(self):
        """Test recording partial payment and then remaining payment via HTMX updates balance and history."""
        session = self.client.session
        session['site_lang'] = 'en'
        session.save()
        bill = Bill.objects.create(
            bill_number='VG-2026-0093',
            client_name='Shri Ram Traders (श्री राम ट्रेडर्स)',
            client_phone='9826011111',
            base_amount=Decimal('5000.00'),
            total_amount=Decimal('5000.00'),
            amount_paid=Decimal('0.00'),
            payment_status=PaymentStatus.UNPAID,
            created_by=self.user,
        )
        url = reverse('billing:bill_payment_update', kwargs={'pk': bill.pk})

        # 1. Record partial payment of 2000 via UPI
        res_partial = self.client.post(url, {
            'amount': '2000.00',
            'payment_method': 'UPI',
            'reference': '238910482910',
            'note': 'GPay payment',
        }, HTTP_HX_REQUEST='true')

        self.assertEqual(res_partial.status_code, 200)
        bill.refresh_from_db()
        self.assertEqual(bill.amount_paid, Decimal('2000.00'))
        self.assertEqual(bill.balance_amount, Decimal('3000.00'))
        self.assertEqual(bill.payment_status, PaymentStatus.PARTIAL)

        # Check partial response contents
        self.assertContains(res_partial, 'Payment of ₹2,000 recorded successfully.')
        self.assertContains(res_partial, '238910482910')
        self.assertContains(res_partial, '₹3,000')

        # Check PaymentSubmission created and verified
        sub = bill.payment_submissions.first()
        self.assertIsNotNone(sub)
        self.assertEqual(sub.amount, Decimal('2000.00'))
        self.assertEqual(sub.status, 'verified')
        self.assertEqual(sub.utr_number, '238910482910')

        # 2. Record remaining 3000 via Cash
        res_full = self.client.post(url, {
            'amount': '3000.00',
            'payment_method': 'Cash',
            'reference': '',
            'note': 'Cash collected at office',
        }, HTTP_HX_REQUEST='true')

        self.assertEqual(res_full.status_code, 200)
        bill.refresh_from_db()
        self.assertEqual(bill.amount_paid, Decimal('5000.00'))
        self.assertEqual(bill.balance_amount, Decimal('0.00'))
        self.assertEqual(bill.payment_status, PaymentStatus.PAID)

        # Invoice fully paid banner rendered, record payment form omitted
        self.assertContains(res_full, 'This invoice is fully paid. No balance due.')

    def test_bill_detail_view_rendering(self):
        """Test bill detail page renders breadcrumbs, two-column details, actions row and payment history."""
        bill = Bill.objects.create(
            bill_number='VG-2026-0094',
            client_name='Patel Automobiles (पटेल ऑटोमोबाइल्स)',
            client_phone='9826022222',
            edition_name=EditionChoice.INDORE,
            placement_type=PlacementType.INSIDE_QUARTER,
            page_number='Page 4',
            base_amount=Decimal('4200.00'),
            total_amount=Decimal('4200.00'),
            amount_paid=Decimal('1000.00'),
            payment_status=PaymentStatus.PARTIAL,
            created_by=self.user,
        )
        url = reverse('billing:bill_detail', kwargs={'pk': bill.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Breadcrumbs & Title
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'VG-2026-0094')

        # Two-column key-value items
        self.assertContains(response, 'Patel Automobiles')
        self.assertContains(response, 'पटेल ऑटोमोबाइल्स')
        self.assertContains(response, '9826022222')
        self.assertContains(response, 'Indore')
        self.assertContains(response, 'Inside Page — Quarter')
        self.assertContains(response, 'Page 4')
        self.assertContains(response, '₹4,200')
        self.assertContains(response, '₹1,000')
        self.assertContains(response, '₹3,200')

        # Actions row
        self.assertContains(response, 'English PDF')
        self.assertContains(response, 'Hindi PDF')
        self.assertContains(response, 'WhatsApp reminder')
        self.assertContains(response, 'Customer portal')

        # Record payment form prefilled with balance 3200
        self.assertContains(response, '3200')

        # Payment history lists initial 1000
        self.assertContains(response, 'Payment History')
        self.assertContains(response, '₹1,000')

    def test_pure_english_pdf_rendering(self):
        """Test that ?lang=en renders a 100% pure English invoice with zero mixed Hindi labels."""
        bill = Bill.objects.create(
            bill_number='VG-2026-9001',
            client_name='पटेल ऑटोमोबाइल्स (Patel Automobiles)',
            client_phone='9826011111',
            placement_type=PlacementType.FRONT_FULL,
            edition_name=EditionChoice.INDORE,
            base_amount=Decimal('5000.00'),
            amount_paid=Decimal('0.00'),
            payment_status=PaymentStatus.UNPAID,
            edition_date='2026-11-03'
        )
        url = reverse('billing:bill_pdf', args=[bill.pk]) + '?lang=en&sign=0'
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        # Check pure English labels
        self.assertContains(res, 'ADVERTISEMENT INVOICE')
        self.assertContains(res, 'Invoice No:')
        self.assertContains(res, 'Advertiser Details (Billed To)')
        self.assertContains(res, 'Patel Automobiles')  # Isolated English client name
        self.assertContains(res, 'Publication & Insertion Details')
        self.assertContains(res, 'Description & Particulars')
        self.assertContains(res, 'Rate (₹)')
        self.assertContains(res, 'Amount in Words:')
        self.assertContains(res, 'Gross Ad Charges:')
        self.assertContains(res, 'Net Payable Total:')
        self.assertContains(res, 'Bank Transfer Details (NEFT / RTGS):')
        self.assertContains(res, 'DIGITALLY VERIFIED')
        self.assertContains(res, 'PAYMENT DUE — PAYABLE:')

        # Ensure no Hindi labels leaked into pure English document
        self.assertNotContains(res, 'विज्ञापन देयक')
        self.assertNotContains(res, 'बिल क्रमांक:')
        self.assertNotContains(res, 'विज्ञापनदाता विवरण')
        self.assertNotContains(res, 'राशि शब्दों में:')
        self.assertNotContains(res, 'कम्प्यूटरीकृत प्रमाणित')

    def test_pure_hindi_pdf_rendering(self):
        """Test that ?lang=hi renders a 100% pure Hindi invoice with zero mixed English labels."""
        bill = Bill.objects.create(
            bill_number='VG-2026-9002',
            client_name='पटेल ऑटोमोबाइल्स (Patel Automobiles)',
            client_phone='9826011111',
            placement_type=PlacementType.FRONT_FULL,
            edition_name=EditionChoice.INDORE,
            base_amount=Decimal('5000.00'),
            amount_paid=Decimal('5000.00'),
            payment_status=PaymentStatus.PAID,
            edition_date='2026-11-03'
        )
        url = reverse('billing:bill_pdf', args=[bill.pk]) + '?lang=hi&sign=0'
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        # Check pure Hindi labels
        self.assertContains(res, 'विज्ञापन देयक')
        self.assertContains(res, 'बिल क्रमांक:')
        self.assertContains(res, 'विज्ञापनदाता विवरण (बिल धारक)')
        self.assertContains(res, 'पटेल ऑटोमोबाइल्स')  # Isolated Hindi client name
        self.assertContains(res, 'प्रकाशन व संस्करण विवरण')
        self.assertContains(res, 'विज्ञापन विवरण एवं प्रकाशन ब्यौरा')
        self.assertContains(res, 'दर (₹)')
        self.assertContains(res, 'राशि शब्दों में:')
        self.assertContains(res, 'मूल विज्ञापन शुल्क:')
        self.assertContains(res, 'कुल देय राशि:')
        self.assertContains(res, 'बैंक खाता विवरण (NEFT / RTGS):')
        self.assertContains(res, 'कम्प्यूटरीकृत प्रमाणित')
        self.assertContains(res, 'पूर्ण भुगतान प्राप्त — खाता चुकता')

        # Ensure no English main labels leaked into pure Hindi document
        self.assertNotContains(res, 'ADVERTISEMENT INVOICE')
        self.assertNotContains(res, 'Invoice No:')
        self.assertNotContains(res, 'Advertiser Details (Billed To)')
        self.assertNotContains(res, 'Gross Ad Charges:')
        self.assertNotContains(res, 'DIGITALLY VERIFIED')

