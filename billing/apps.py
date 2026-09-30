from django.apps import AppConfig


class BillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'billing'
    verbose_name = 'विश्वगुरु विज्ञापन बिलिंग (Vishwaguru Billing)'

    def ready(self):
        from django.db.backends.signals import connection_created

        def configure_sqlite(sender, connection, **kwargs):
            if connection.vendor == 'sqlite':
                with connection.cursor() as cursor:
                    cursor.execute('PRAGMA journal_mode = WAL;')
                    cursor.execute('PRAGMA synchronous = NORMAL;')
                    cursor.execute('PRAGMA busy_timeout = 20000;')

        connection_created.connect(configure_sqlite)
