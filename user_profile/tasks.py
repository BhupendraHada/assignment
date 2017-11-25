import logging
from celery import Celery
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
app = Celery('tasks', broker="amqp://guest:guest@localhost:5672/")
from assignment.settings import EMAIL_HOST_USER


@app.task
def send_verification_email(user_id, recipients_list):
    UserModel = get_user_model()
    try:
        user = UserModel.objects.get(pk=user_id)
        msg = "Hi " + str(user.username) + ", Your profile successfully registered."
        send_mail("User Registration Confirmation", msg, EMAIL_HOST_USER, recipients_list)
    except UserModel.DoesNotExist:
        logging.warning("Tried to send verification email to non-existing user '%s'" % user_id)
    except Exception as e:
        logging.warning("Error to send verification email: '%s'" % e.__str__())