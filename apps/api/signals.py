import os

from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string

from django_rest_passwordreset.signals import reset_password_token_created

from .models import User, AccountActivationToken


@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    if created and not instance.is_staff:
        token = get_random_string(length=128)
        AccountActivationToken.objects.create(user=instance, token=token)

        send_activation_email(instance, token)


def send_activation_email(user, token):
    base_url = os.environ['BASE_URL']
    endpoint = os.environ['ACTIVATION_ENDPOINT']
    contact_email = os.environ['CONTACT_EMAIL']
    logo_url = 'https://i.imgur.com/NF0825u.png'

    context = {
        'current_user': user,
        'user_name': user.name,
        'user_email': user.email,
        'contact_email': contact_email,
        'activation_url': "{}/{}".format(
            base_url + endpoint, 
            token
        ),
        'logo_url': logo_url
    }
    print(f'context = {context}')

    email_html_message = render_to_string(
        'email/user_activation.html', 
        context
    )

    msg = EmailMultiAlternatives(
        # title
        "Activar cuenta",
        # message
        email_html_message,
        # from
        contact_email,
        # to
        [user.email]
    )

    msg.attach_alternative(email_html_message, "text/html")
    msg.send()


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, 
    instance, 
    reset_password_token, 
    *args, 
    **kwargs
):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    base_url = os.environ['BASE_URL']
    endpoint = os.environ['PASSWORD_RESET_ENDPOINT']
    contact_email = os.environ['CONTACT_EMAIL']
    logo_url = 'https://i.imgur.com/NF0825u.png'

    context = {
        'current_user': reset_password_token.user,
        'user_name': reset_password_token.user.name,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}/{}".format(
            instance.request.build_absolute_uri(base_url + endpoint),
            reset_password_token.key
        ),
        'logo_url': logo_url
    }

    email_html_message = render_to_string(
        'email/password_reset.html', 
        context
    )

    msg = EmailMultiAlternatives(
        # title
        "Se ha solicitado restablecer su contraseña",
        # message
        email_html_message,
        # from
        contact_email,
        # to
        [reset_password_token.user.email]
    )

    msg.attach_alternative(email_html_message, "text/html")
    msg.send()


@receiver(post_save, sender=User)
def send_password_change_email(sender, instance, **kwargs):
    if instance.pk is not None:
        original_user = User.objects.get(pk=instance.pk)
        if instance.password != original_user.password:
            # La contraseña del usuario ha sido modificada
            contact_email = os.environ['CONTACT_EMAIL']
            logo_url = 'https://i.imgur.com/NF0825u.png'

            context = {
                'current_user': instance,
                'user_name': instance.name,
                'user_email': instance.email,
                'contact_email': contact_email,
                'logo_url': logo_url
            }

            email_html_message = render_to_string(
                'email/password_reset_confirm.html', 
                context
            )

            msg = EmailMultiAlternatives(
                # title
                "Su contraseña ha sido modificada",
                # message
                email_html_message,
                # from
                contact_email,
                # to
                [instance.email]
            )
            msg.attach_alternative(email_html_message, "text/html")
            msg.send()


@receiver(pre_save, sender=User)
def send_user_deactivation_email(sender, instance, **kwargs):
    # Verifica si el estado de activación ha cambiado
    if instance.pk is not None:
        original_user = User.objects.get(pk=instance.pk)
        if original_user.is_active and not instance.is_active:
            # El usuario se ha desactivado
            contact_email = os.environ['CONTACT_EMAIL']
            logo_url = 'https://i.imgur.com/NF0825u.png'

            context = {
                'current_user': instance,
                'user_name': instance.name,
                'user_email': instance.email,
                'contact_email': contact_email,
                'logo_url': logo_url
            }

            email_html_message = render_to_string(
                'email/user_deactivation.html', 
                context
            )

            msg = EmailMultiAlternatives(
                # title
                "Su cuenta ha sido desactivada",
                # message
                email_html_message,
                # from
                contact_email,
                # to
                [instance.email]
            )

            msg.attach_alternative(email_html_message, "text/html")
            msg.send()


@receiver(pre_delete, sender=User)
def send_user_signout_email(sender, instance, **kwargs):
    # Verifica si la contraseña ha sido modificada
    if instance.password != kwargs['raw']:
        contact_email = os.environ['CONTACT_EMAIL']
        logo_url = 'https://i.imgur.com/NF0825u.png'

        context = {
            'current_user': instance,
            'user_name': instance.name,
            'user_email': instance.email,
            'contact_email': contact_email,
            'logo_url': logo_url
        }

        email_html_message = render_to_string(
            'email/user_deletion.html', 
            context
        )

        msg = EmailMultiAlternatives(
            # title
            "Su cuenta ha sido eliminada",
            # message
            email_html_message,
            # from
            contact_email,
            # to
            [instance.email]
        )
        
        msg.attach_alternative(email_html_message, "text/html")
        msg.send()
