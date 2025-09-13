from django.db import models
from django.core.cache import cache
from django.db import models

from users.models import User

class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    full_name = models.CharField(max_length=255, verbose_name='Ф.И.О.')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец')

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        permissions = [
            ('view_all_clients', 'Can view all clients'),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.invalidate_cache()

    def delete(self, *args, **kwargs):
        self.invalidate_cache()
        super().delete(*args, **kwargs)

    def invalidate_cache(self):
        """Инвалидация связанного кэша"""
        cache_key = f'user_clients_{self.owner.id}'
        cache.delete(cache_key) 


    def __str__(self):
        return self.full_name

class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Тело письма')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        permissions = [
            ('view_all_messages', 'Can view all messages'),
        ]

    def __str__(self):
        return self.subject

class Mailing(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
    ]

    start_time = models.DateTimeField(verbose_name='Дата и время первой отправки')
    end_time = models.DateTimeField(verbose_name='Дата и время окончания отправки')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='created', verbose_name='Статус')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='Сообщение')
    clients = models.ManyToManyField(Client, verbose_name='Клиенты')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        permissions = [
            ('view_all_mailings', 'Can view all mailings'),
            ('disable_mailing', 'Can disable mailing'),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.invalidate_cache()

    def delete(self, *args, **kwargs):
        self.invalidate_cache()
        super().delete(*args, **kwargs)

    def invalidate_cache(self):
        """Инвалидация связанного кэша"""
        # Статистика пользователя
        cache_key = f'mailing_stats_{self.owner.id}'
        cache.delete(cache_key)

        # Кэш списка рассылок
        cache_key = f'user_mailings_{self.owner.id}'
        cache.delete(cache_key)

        # Кэш деталей рассылки
        cache_key = f'mailing_detail_{self.id}'
        cache.delete(cache_key)

    def __str__(self):
        return f"Рассылка {self.id} ({self.status})"

class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('failure', 'Не успешно'),
    ]

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name='Рассылка')
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время попытки')
    status = models.CharField(max_length=7, choices=STATUS_CHOICES, verbose_name='Статус')
    server_response = models.TextField(blank=True, null=True, verbose_name='Ответ сервера')

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылки'

    def __str__(self):
        return f"Попытка {self.mailing_id} - {self.status}"

