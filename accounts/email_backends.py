import logging

from django.core.mail.backends.smtp import EmailBackend

logger = logging.getLogger('accounts.email')


class DebugSMTPEmailBackend(EmailBackend):
    def send_messages(self, email_messages):
        messages = list(email_messages)
        logger.info(
            'SMTP send started; message_count=%d; host=%s; port=%s; tls=%s',
            len(messages),
            self.host,
            self.port,
            self.use_tls,
        )
        try:
            sent_count = super().send_messages(messages)
        except Exception as error:
            logger.error('SMTP send failed; error_type=%s', type(error).__name__)
            raise

        logger.info(
            'SMTP send finished; accepted_count=%d; message_count=%d',
            sent_count,
            len(messages),
        )
        return sent_count
