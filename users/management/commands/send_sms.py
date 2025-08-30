from django.core.management.base import BaseCommand
from users.utils import send_sms

class Command(BaseCommand):
    help = 'Отправляет тестовое SMS на указанный номер'

    def handle(self, *args, **options):
        number = '+79119497220'
        message = 'Салют от csu'
        response = send_sms(number, message)
        status_code = response.get('status_code', '')
        print(f"Status code: {status_code}")
        print(f"Response body: {response}")

        number = '+79219426679'
        message = 'Салют от csu на мегафон'
        response = send_sms(number, message)
        status_code = response.get('status_code', '')
        print(f"Status code: {status_code}")
        print(f"Response body: {response}")

        number = '+79118388645'
        message = 'Салют от csu на МТС'
        response = send_sms(number, message)
        status_code = response.get('status_code', '')
        print(f"Status code: {status_code}")
        print(f"Response body: {response}")