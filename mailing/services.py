from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from .models import MailingAttempt, Mailing
import logging

logger = logging.getLogger(__name__)


def get_cached_mailing_stats(user):
    """Получение статистики рассылок с кэшированием"""
    cache_key = f'mailing_stats_{user.id}'
    stats = cache.get(cache_key)

    if stats is None:
        user_mailings = Mailing.objects.filter(owner=user)

        total_attempts = MailingAttempt.objects.filter(mailing__in=user_mailings).count()
        successful_attempts = MailingAttempt.objects.filter(
            mailing__in=user_mailings, status='success'
        ).count()
        failed_attempts = total_attempts - successful_attempts

        stats = {
            'total_mailings': user_mailings.count(),
            'active_mailings': user_mailings.filter(status='started').count(),
            'total_attempts': total_attempts,
            'successful_attempts': successful_attempts,
            'failed_attempts': failed_attempts,
            'success_rate': (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0,
        }

        cache.set(cache_key, stats, 120)

    return stats


def invalidate_mailing_stats_cache(user):
    """Инвалидация кэша статистики"""
    cache_key = f'mailing_stats_{user.id}'
    cache.delete(cache_key)


def send_mailing(mailing):
    """Функция отправки рассылки с кэшированием статуса"""
    cache_key = f'mailing_status_{mailing.id}'

    # Проверяем, не отправляется ли уже рассылка
    if cache.get(cache_key):
        logger.warning(f'Рассылка {mailing.id} уже отправляется')
        return

    cache.set(cache_key, 'sending', 300)

    try:
        clients = mailing.clients.all()
        message = mailing.message

        for client in clients:
            try:
                send_mail(
                    subject=message.subject,
                    message=message.body,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[client.email],
                    fail_silently=False,
                )

                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='success',
                    server_response='Email успешно отправлен'
                )

            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='failure',
                    server_response=str(e)
                )

        invalidate_mailing_stats_cache(mailing.owner)

    finally:
        cache.delete(cache_key)
