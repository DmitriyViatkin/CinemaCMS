from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os # Для чтения файла шаблона

def send_campaign_email(email_campaign_obj, user_email):
    """
    Отправляет Email для конкретной кампании заданному пользователю.

    Args:
        email_campaign_obj: Объект Email_campaing, содержащий информацию о кампании.
        user_email: Email-адрес получателя.
    """
    # Проверяем, есть ли шаблон у кампании
    if not email_campaign_obj.template:
        print(f"Ошибка: Кампания #{email_campaign_obj.id} не имеет привязанного шаблона.")
        return False

    # Проверяем, существует ли файл шаблона
    if not email_campaign_obj.template.template_file:
        print(f"Ошибка: Шаблон #{email_campaign_obj.template.id} не имеет связанного файла.")
        return False

    try:
        # Получаем путь к файлу шаблона
        template_file_path = email_campaign_obj.template.template_file.path

        # Читаем содержимое файла шаблона
        with open(template_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Если вы хотите передать контекст в шаблон (например, имя пользователя)
        # context = {'user_name': user.first_name if user.first_name else user.username,
        #            'campaign_id': email_campaign_obj.id}
        # html_content = render_to_string('path/to/your_template_base.html', context)
        # В вашем случае, так как шаблон загружается файлом, вам нужно будет парсить его вручную
        # или обеспечить, чтобы он уже содержал нужные данные, или использовать
        # jinja2/django_jinja для рендеринга вне view

        # Создаем текстовую версию Email (для клиентов, которые не отображают HTML)
        text_content = strip_tags(html_content) # Удаляем HTML-теги для текстовой версии

        subject = f"Ваше сообщение от кампании #{email_campaign_obj.id}" # Тема письма
        from_email = None # Использует DEFAULT_FROM_EMAIL из settings.py

        msg = EmailMultiAlternatives(subject, text_content, from_email, [user_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        print(f"Email для кампании #{email_campaign_obj.id} успешно отправлен на {user_email}")
        return True

    except Exception as e:
        print(f"Ошибка при отправке Email для кампании #{email_campaign_obj.id} на {user_email}: {e}")
        return False
