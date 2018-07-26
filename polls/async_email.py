from django.core.mail import send_mail as core_send_mail
from django.core.mail import EmailMultiAlternatives
import threading

class EmailThread(threading.Thread):
    def __init__(self, subject, message, from_email, recipient_list, fail_silently):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        self.from_email = from_email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run (self):
        core_send_mail(self.subject, self.message, self.from_email, self.recipient_list, self.fail_silently)



    