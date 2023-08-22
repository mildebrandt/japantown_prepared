import os

from typing import List, Optional
from smtplib import SMTP, SMTP_SSL

from email.message import EmailMessage
from email.utils import formataddr
from .config import config

SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")


def sendmail(
    sender_email: str,
    smtp_host: str = "localhost",
    smtp_port: int = 25,
    smtp_username: Optional[str] = None,
    smtp_password: Optional[str] = None,
    sender_name: Optional[str] = None,
    to: Optional[List[str]] = None,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    subject: Optional[str] = None,
    text_body: Optional[str] = None,
    html_body: Optional[str] = None,
    ssl: bool = True,
    **kwargs,
):
    if to is None and cc is None and bcc is None:
        raise Exception("No receivers for the email.")

    if text_body is None and html_body is None:
        raise Exception("No body for the email.")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((sender_name, sender_email))

    if to is not None:
        msg["To"] = ", ".join(to)
    else:
        to = []

    if cc is not None:
        msg["Cc"] = ", ".join(cc)
    else:
        cc = []

    if bcc is not None:
        msg["Bcc"] = ", ".join(bcc)
    else:
        bcc = []

    if text_body is None:
        msg.set_content(html_body, "html")
    else:
        msg.set_content(text_body, "plain")

        if html_body is not None:
            msg.add_alternative(html_body, "html")

    if ssl:
        SMTPClass = SMTP_SSL
    else:
        SMTPClass = SMTP

    with SMTPClass(smtp_host, smtp_port) as server:
        if smtp_username is not None:
            server.login(smtp_username, smtp_password)
        server.send_message(msg)


def nofity(subject, msg):
    args = config["notify"]
    args["subject"] = subject
    args["text_body"] = msg

    if SMTP_USERNAME:
        args["smtp_username"] = SMTP_USERNAME

    if SMTP_PASSWORD:
        args["smtp_password"] = SMTP_PASSWORD

    sendmail(**args)


# Used only for testing
if __name__ == "__main__":
    nofity("Test message", "Test message\n\nanother line")
