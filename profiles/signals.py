from django.db.models.signals import post_save
from django.dispatch import receiver

from authentication.models import User
from profiles.models import Profile, TypeUser


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_staff:
            user_type = TypeUser.ADMIN.value
        else:
            user_type = TypeUser.USER.value

        Profile.objects.create(user=instance, user_type=user_type)
