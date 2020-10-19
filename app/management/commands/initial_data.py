from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import IntegrityError

from app.models import Option


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            Option(key='is_camera_on', value=False).save()
            Option(key='is_send_email', value=False).save()
            Option(key='with_photo', value=False).save()
            Option(key='is_minute', value=False).save()
            user = User(username='admin', first_name='Saye', last_name='Banayee')
            user.set_password('123456')
            user.save()
        except IntegrityError as e:
            pass
