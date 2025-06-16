from celery import shared_task
from .send_email import send_campaign_email
from users.models import Email_campaing
from celery_progress.backend import ProgressRecorder

@shared_task(bind=True)
def send_campaign_emails_task(self, campaign_id, recipient_list):
    """
    Задача Celery для отправки писем кампании нескольким получателям.
    """
    email_campaign_obj = None
    progress_recorder = ProgressRecorder(self)
    try:
        email_campaign_obj = Email_campaing.objects.get(id=campaign_id)
    except Email_campaing.DoesNotExist:
        print(f"Ошибка: Кампания с ID {campaign_id} не найдена.")
        return False

    i = 0
    count = len(recipient_list)
    for recipient_email in recipient_list:
        success = send_campaign_email(email_campaign_obj, recipient_email)
        if success:

            print(f"Email кампании '#{email_campaign_obj.id}' успешно отправлен на {recipient_email}")
            persent = (i/count)*100
            progress_recorder.set_progress(i + 1, count, f'відправлено листів     {round(persent)} %')
        else:

            print(f"Ошибка при отправке Email кампании '#{email_campaign_obj.id}' на {recipient_email}")
        i += 1

    try:
        email_campaign_obj.status = 'sent'
        email_campaign_obj.save()
        print(f"DEBUG: Кампания ID {campaign_id} завершила отправку писем и статус обновлен на 'sent'.")
    except Exception as e:
        print(f"Ошибка при обновлении статуса кампании {campaign_id}: {e}")

    return True
