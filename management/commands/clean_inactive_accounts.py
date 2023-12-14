from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone
from apps.api.models import User, AccountActivationToken, Pictograma, Audio, Rutina


class Command(BaseCommand):
    help = 'Elimina cuentas de usuario inactivas'

    def handle(self, *args, **options):
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        hundred_days_ago = timezone.now() - timezone.timedelta(days=100)

        accounts_to_delete = User.objects.filter(
            models.Q(is_active=False, inactive_since__lt=thirty_days_ago) |
            models.Q(is_active=False, created_at__lt=thirty_days_ago) |
            models.Q(last_login__lt=hundred_days_ago)
        )

        for user in accounts_to_delete:
            # Elimina el contenido asociado (por ejemplo, posts)
            Pictograma.objects.filter(autor=user).delete()
            Audio.objects.filter(autor=user).delete()
            Rutina.objects.filter(autor=user).delete()
            AccountActivationToken.objects.filter(user=user).delete()

            # Elimina el usuario
            user.delete()

        self.stdout.write(self.style.SUCCESS('Cuentas inactivas eliminadas con éxito.'))
