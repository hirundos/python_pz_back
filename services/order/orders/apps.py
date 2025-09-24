from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'orders'
    label = 'orders'  # 명시적 레이블 설정
    verbose_name = 'Orders'

    def ready(self):
        """앱이 준비될 때 호출되는 메서드"""
        pass
