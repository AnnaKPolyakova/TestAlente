from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_email(event, email, review=None):
    message = {
        "event": event.title,
        "date": event.start_at,
        "email": email,
    }
    if review:
        message["message"] = "Поступил новый отзыв на событие!"
        subject = "Новый отзыв на событие"
    else:
        message["message"] = "Поступила новая заявка на участие!"
        subject = "Новая заявка на событие"
    html_message = render_to_string("email.html", message)
    message = EmailMessage(
        subject,
        html_message,
        to=[event.user.email],
    )
    message.content_subtype = "html"
    message.send()
