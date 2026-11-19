import logging

from anymail.backends.resend import EmailBackend as ResendEmailBackend

logger = logging.getLogger('accounts.email')


class DebugResendEmailBackend(ResendEmailBackend):
    def send_messages(self, email_messages):
        messages = list(email_messages)
        logger.info(
            'Resend API send started; message_count=%d',
            len(messages),
        )
        try:
            sent_count = super().send_messages(messages)
        except Exception as error:
            logger.error('Resend API send failed; error_type=%s', type(error).__name__)
            raise

        logger.info(
            'Resend API send finished; accepted_count=%d; message_count=%d',
            sent_count,
            len(messages),
        )
        return sent_count
