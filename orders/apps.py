from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
    
    def ready(self):
        """Import signals when the app is ready"""
        try:
            import orders.signals
        except ImportError:
            pass
