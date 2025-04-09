from celery import shared_task
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO


@shared_task
def image_shop_data_task(file_path):
    from .utils.import_data import import_shop_data
    import_shop_data(file_path)


@shared_task
def send_email_task(subject, message, from_email, recipient_list):
    from django.core.mail import send_mail
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)