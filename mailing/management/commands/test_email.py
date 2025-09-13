from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Test email sending functionality'

    def handle(self, *args, **options):
        try:
            send_mail(
                subject='Тестовое письмо от сервиса рассылок',
                message='Это тестовое письмо для проверки работы email-рассылок.\n\nС уважением,\nСервис рассылок',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['test@example.com'],  # замените на реальный email
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS('Тестовое письмо успешно отправлено!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка отправки письма: {e}')
            )

