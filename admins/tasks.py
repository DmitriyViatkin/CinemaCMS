from celery import shared_task
from .send_email import send_campaign_email
from users.models import Email_campaing

@shared_task
def send_campaign_emails_task(campaign_id, recipient_list):
    """
    Задача Celery для отправки писем кампании нескольким получателям.
    """
    try:
        # Получаем объект EmailCampaign по ID
        email_campaign_obj = Email_campaing.objects.get(id=campaign_id)
    except Email_campaing.DoesNotExist:
        print(f"Ошибка: Кампания с ID {campaign_id} не найдена.")
        return False

    for recipient_email in recipient_list:
        success = send_campaign_email(email_campaign_obj, recipient_email)
        if success:
            print(f"Email кампании '{email_campaign_obj.subject}' успешно отправлен на {recipient_email}")
        else:
            print(f"Ошибка при отправке Email кампании '{email_campaign_obj.subject}' на {recipient_email}")

    return True