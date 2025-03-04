from django.apps import AppConfig


class FrontendAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "frontend_app"


    
    def ready(self):
        import frontend_app.signals  