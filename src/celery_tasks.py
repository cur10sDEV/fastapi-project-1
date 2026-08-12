from asgiref.sync import async_to_sync
from celery import Celery
from pydantic import NameEmail

from src.mail.main import (
    send_user_verification_message,
    send_password_reset_request_message,
)
from src.mail.schemas import MailSubjectTypes

celery_app = Celery()

celery_app.config_from_object("src.config")


@celery_app.task()
def send_mail(mail_type: str, username: str, email: NameEmail, token: str):
    print(mail_type)
    if mail_type == MailSubjectTypes.ACCOUNT_VERIFICATION:
        async_to_sync(send_user_verification_message)(username, email, token)

    elif mail_type == MailSubjectTypes.RESET_PASSWORD_REQUEST:
        async_to_sync(send_password_reset_request_message)(username, email, token)
