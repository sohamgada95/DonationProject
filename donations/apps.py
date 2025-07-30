from django.apps import AppConfig


class DonationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'donations'

    def ready(self):
        # Disable last_login updates to prevent database writes on Vercel
        from django.contrib.auth.models import update_last_login
        from django.contrib.auth import user_logged_in
        user_logged_in.disconnect(update_last_login)