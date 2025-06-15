from django.core.mail import send_mail, EmailMultiAlternatives

from django.utils.html import strip_tags


def send_campaign_email(email_campaign_obj, user_email):
    """
    Отправляет Email для конкретной кампании заданному пользователю.

    Args:
        email_campaign_obj: Объект Email_campaing, содержащий информацию о кампании.
        user_email: Email-адрес получателя.
    """
    #
    if not email_campaign_obj.template:
        print(f"Ошибка: Кампания #{email_campaign_obj.id} не имеет привязанного шаблона.")
        return False

    #
    if not email_campaign_obj.template.template_file:
        print(f"Ошибка: Шаблон #{email_campaign_obj.template.id} не имеет связанного файла.")
        return False

    try:
        #
        template_file_path = email_campaign_obj.template.template_file.path

        #
        with open(template_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()


        text_content = strip_tags(html_content)

        subject = f"Ваше сообщение от кампании #{email_campaign_obj.id}"
        from_email = None

        msg = EmailMultiAlternatives(subject, text_content, from_email, [user_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        print(f"Email для кампании #{email_campaign_obj.id} успешно отправлен на {user_email}")
        return True

    except Exception as e:
        print(f"Ошибка при отправке Email для кампании #{email_campaign_obj.id} на {user_email}: {e}")
        return False
