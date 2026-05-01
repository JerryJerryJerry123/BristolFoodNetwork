from django.apps import AppConfig
import sys


class MarketplaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'marketplace'

    def ready(self):
        # Only run when using runserver (not migrate, shell, etc.)
        if 'runserver' in sys.argv:
            from django.core.management import call_command
            print("Running daily delivery simulation...")
            call_command('run_daily_deliveries')