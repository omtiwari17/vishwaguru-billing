from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from billing import views as billing_views

def root_redirect(request):
    return redirect('billing:dashboard')

def accounts_login_redirect(request):
    return redirect('login')

urlpatterns = [
    path('', root_redirect, name='root_redirect'),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='billing/login.html'), name='login'),
    path('accounts/login/', accounts_login_redirect, name='accounts_login_redirect'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Direct short links for customer statement portal
    path('statement/<uuid:token>/', billing_views.customer_portal, name='customer_portal_root'),
    path('c/<uuid:token>/', billing_views.customer_portal_short, name='customer_portal_short_root'),
    path('bills/', include('billing.urls', namespace='billing')),
]
