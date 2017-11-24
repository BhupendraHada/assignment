import logging
from celery import Celery
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model
app = Celery('tasks', broker="amqp://guest:guest@localhost:5672/")
from assignment.settings import EMAIL_HOST_USER


@app.task
def send_verification_email(user_id, recipients_list):
    UserModel = get_user_model()
    try:
        user = UserModel.objects.get(pk=user_id)
        mail_obj = EmailMultiAlternatives("User Registration Confirmation", "Hi User, <p>Your profile successfully registered.</p>", EMAIL_HOST_USER, recipients_list, cc=[], bcc=[])
        mail_obj.attach_alternative("Hi User, <p>Your profile successfully registered.</p>", "text/html")
        mail_obj.send()
    except UserModel.DoesNotExist:
        logging.warning("Tried to send verification email to non-existing user '%s'" % user_id)
    except Exception as e:
        logging.warning("Error to send verification email: '%s'" % e.__str__())