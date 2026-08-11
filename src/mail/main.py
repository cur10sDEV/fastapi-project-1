from datetime import date

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import NameEmail

from src.config import app_config
from .schemas import MailSubjectTypes
from .templates import USER_VERIFICATION_MAIL_TEMPLATE

# BASE_DIR = Path(__file__).resolve().parent


mail_config = ConnectionConfig(
    MAIL_USERNAME=app_config.MAIL_USERNAME,
    MAIL_PASSWORD=app_config.MAIL_PASSWORD,
    MAIL_FROM=app_config.MAIL_FROM,
    MAIL_PORT=app_config.MAIL_PORT,
    MAIL_SERVER=app_config.MAIL_SERVER,
    MAIL_FROM_NAME=app_config.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    # TEMPLATE_FOLDER=Path(BASE_DIR, "templates"),
)

mail = FastMail(config=mail_config)


def create_message(recipients: list[NameEmail], subject: str, body: str):
    message = MessageSchema(
        recipients=recipients, subject=subject, body=body, subtype=MessageType.html
    )

    return message


def create_user_verification_url(token: str):
    return f"{app_config.DOMAIN}/api/v1/auth/verify/{token}"


async def send_user_verification_message(
    username: str,
    email: NameEmail,
    verification_token: str,
):
    message_body = (
        USER_VERIFICATION_MAIL_TEMPLATE.replace("{{user_name}}", username)
        .replace(
            "{{verification_url}}",
            create_user_verification_url(verification_token),
        )
        .replace("{{app_name}}", app_config.NAME)
        .replace("{{app_url}}", app_config.DOMAIN)
        .replace(
            "{{expiry_time}}", f"{app_config.VERIFICATION_MAIL_EXPIRY / 3600} hours"
        )
        .replace("{{year}}", f"{date.today().year}")
    )

    message = create_message(
        recipients=[email],
        subject=MailSubjectTypes.ACCOUNT_VERIFICATION,
        body=message_body,
    )

    await mail.send_message(message=message)
