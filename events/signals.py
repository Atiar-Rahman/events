from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import Event

@receiver(m2m_changed, sender=Event.participants.through)
def send_rsvp_confirmation_email(sender, instance, action, pk_set, **kwargs):
    """
    Sends a confirmation email to each user who RSVP'd to an event.
    Triggered when a User is added to Event.participants (RSVP).
    """
    if action == 'post_add':
        for user_id in pk_set:
            try:
                user = User.objects.get(pk=user_id)
                send_mail(
                    subject='RSVP Confirmation',
                    message=f'Thank you {user.first_name or user.username} for RSVPing to "{instance.name}"!',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except User.DoesNotExist:
                pass
