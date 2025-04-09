from django.core.management.base import BaseCommand
from ...utils.import_data import import_shop_data
from backend.tasks import image_shop_data_task
import yaml

class Command(BaseCommand):
    help = 'Загружает данные из YAML файла'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Путь к YAML файлу')

    def handle(self, *args, **options):
        file_path = options['file_path']
        try:
            image_shop_data_task.delay(file_path)
            self.stdout.write(self.style.SUCCESS('Данные импортированы!'))
        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {str(e)}'))
        except yaml.YAMLError as e:
            self.stdout.write(self.style.ERROR(f'Ошибка YAML: {str(e)}'))
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'Ошибка в данных: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Неизвестная ошибка: {str(e)}'))