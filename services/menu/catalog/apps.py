from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'catalog'
    label = 'catalog'
    verbose_name = 'Catalog'

    def ready(self):
        """앱이 준비될 때 호출되는 메서드"""
        pass
