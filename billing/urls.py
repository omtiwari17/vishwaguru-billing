from django.urls import path
from billing import views

app_name = 'billing'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('new/', views.bill_create, name='bill_create'),
    path('<int:pk>/', views.bill_detail, name='bill_detail'),
    path('<int:pk>/pdf/', views.bill_pdf_view, name='bill_pdf'),
    path('<int:pk>/update-payment/', views.bill_payment_update, name='bill_payment_update'),
    path('search/', views.bill_search, name='bill_search'),
    path('set-lang/<str:lang_code>/', views.set_site_language, name='set_language'),
    path('api/clients/search/', views.client_search_api, name='client_search_api'),

    # Customer Self-Service Statement Portal & Zero-Fee UPI Payment
    path('statement/<uuid:token>/', views.customer_portal, name='customer_portal'),
    path('c/<uuid:token>/', views.customer_portal_short, name='customer_portal_short'),
    path('statement/<uuid:token>/submit-payment/', views.customer_payment_submit, name='customer_payment_submit'),
    path('statement/<uuid:token>/bill/<int:bill_id>/pdf/', views.customer_bill_pdf, name='customer_bill_pdf'),

    # Staff Verification for Customer UPI Payments
    path('submissions/', views.payment_submissions_list, name='payment_submissions_list'),
    path('submissions/<int:submission_id>/verify/', views.verify_payment_submission, name='verify_payment_submission'),

    # Bank Details & UPI ID Management with Field-Level Encryption
    path('settings/payment-info/', views.payment_info_settings, name='payment_info_settings'),
]

