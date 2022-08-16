import enum
import os
from typing import Union

from django.db import models
from django.utils.translation import gettext_lazy as _

from administration.models import UserPlan
from core.converters.images import image_resize, validate_images
from core.models import TimestampedModel
from authentication.models import User


class TypeUser(enum.Enum):
    USER = "1"
    OWNER_COMPANY = "2"
    MANAGER = "3"
    ADMIN = "4"


# class ProfileSettings(models.Model):
#     background_tree = models.CharField(max_length=100, default="default")


class Profile(TimestampedModel):
    USER = TypeUser.USER.value
    OWNER_COMPANY = TypeUser.OWNER_COMPANY.value
    MANAGER = TypeUser.MANAGER.value
    ADMIN = TypeUser.ADMIN.value
    TYPES_USER = (
        (USER, 'user'),
        (OWNER_COMPANY, 'owner company'),
        (MANAGER, 'manager'),
        (ADMIN, 'admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(db_index=True, max_length=255, null=True, blank=True)
    last_name = models.CharField(db_index=True, max_length=255, null=True, blank=True)
    patronymic = models.CharField(db_index=True, max_length=255, null=True, blank=True)
    avatar = models.ImageField(upload_to="profile/avatars/", null=True, blank=True, validators=[validate_images])
    avatar_thumb = models.ImageField(upload_to="profile/thumb/", null=True, blank=True, validators=[validate_images])
    date_birth = models.DateField(_("date birth"), db_index=True, blank=True, null=True)
    user_type = models.CharField(_('type user'), max_length=2, default=TypeUser.USER.value, choices=TYPES_USER)
    is_banned = models.BooleanField(default=False)
    background_tree = models.CharField(max_length=100, null=True, blank=True)
    tariff = models.ForeignKey(UserPlan, related_name='profiles', null=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        is_new_avatar = kwargs.pop("new_avatar", None)

        if is_new_avatar and self.avatar:
            try:
                this = Profile.objects.get(id=self.id)

            except Profile.DoesNotExist:
                this = None

            if this:
                try:
                    os.remove(this.avatar_thumb.path)
                    os.remove(this.avatar.path)

                except Exception as e:
                    pass

            try:
                file_obj = image_resize(self.avatar, 125, 125, "thumb")
                self.avatar_thumb = file_obj

            except FileNotFoundError:
                pass

        super(Profile, self).save(*args, **kwargs)

    @property
    def name(self) -> Union[str, None]:
        name = " ".join(map(lambda x: str(x), filter(lambda x: bool(x),
                                                     [self.first_name, self.patronymic, self.last_name])))

        if not name:
            return None

        return name
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return f"{self.last_name} {self.first_name[0]}."


class Archive(TimestampedModel):
    profile = models.ForeignKey(Profile, related_name="archives", on_delete=models.CASCADE)
    file = models.FileField(upload_to="archives")


class StatisticProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    disk_space_used = models.IntegerField(default=0)
    count_vertex = models.IntegerField(default=0)
