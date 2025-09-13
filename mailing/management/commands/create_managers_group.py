from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from mailing.models import Mailing, Client, Message


class Command(BaseCommand):
    help = 'Create Managers group with permissions'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='Менеджеры')

        # Добавляем права на просмотр всех объектов
        permissions = [
            'view_all_mailings', 'view_all_clients', 'view_all_messages',
            'view_mailing', 'view_client', 'view_message',
        ]

        for codename in permissions:
            try:
                permission = Permission.objects.get(codename=codename)
                group.permissions.add(permission)
            except Permission.DoesNotExist:
                self.stdout.write(f'Permission {codename} not found')

        self.stdout.write(
            self.style.SUCCESS('Successfully created Managers group with permissions')
        )

