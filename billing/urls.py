from django.urls import path
from billing import views

app_name = 'billing'

urlpatterns = [
    path('new/', views.bill_create, name='bill_create'),
    path('<int:pk>/', views.bill_detail, name='bill_detail'),
    path('<int:pk>/pdf/', views.bill_pdf_view, name='bill_pdf'),
    path('<int:pk>/update-payment/', views.bill_payment_update, name='bill_payment_update'),
    path('search/', views.bill_search, name='bill_search'),
    path('set-lang/<str:lang_code>/', views.set_site_language, name='set_language'),
]
