from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Create groups and assign permissions'

    def handle(self, *args, **options):
        managers_group, created = Group.objects.get_or_create(name='Менеджеры')
        # Права на просмотр всех рассылок, клиентов и сообщений
        view_all_mailings = Permission.objects.get(codename='view_all_mailings')
        managers_group.permissions.add(view_all_mailings)
