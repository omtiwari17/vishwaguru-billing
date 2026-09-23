from django.contrib import admin
from billing.models import Bill, PaymentInfo


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = [
        'bill_number',
        'client_name',
        'client_phone',
        'placement_type',
        'edition_date',
        'total_amount',
        'payment_status',
        'amount_paid',
        'created_at',
    ]
    list_filter = [
        'payment_status',
        'placement_type',
        'edition_name',
        'edition_date',
    ]
    search_fields = [
        'bill_number',
        'client_name',
        'client_phone',
        'ad_title',
        'payment_note',
    ]
    readonly_fields = [
        'bill_number',
        'total_amount',
        'created_at',
        'updated_at',
    ]
    ordering = ['-id']


@admin.register(PaymentInfo)
class PaymentInfoAdmin(admin.ModelAdmin):
    list_display = [
        'newspaper_name',
        'bank_name',
        'account_number',
        'ifsc_code',
        'upi_id',
        'phone_number',
    ]

    def has_add_permission(self, request):
        # Only allow 1 singleton instance
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False
