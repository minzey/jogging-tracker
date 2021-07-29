from django.db import models
from django.contrib.auth.models import AbstractUser

class FitnessUser(AbstractUser):
    """
    User model of Fitness App with 3 roles
    """

    class Role(models.IntegerChoices):
        REGULAR = (0, "Regular")
        USER_MANAGER = (1, "User Manager")
        ADMIN = (2, "Admin")

    role = models.IntegerField(choices=Role.choices, default=Role.REGULAR)

    @property
    def get_role_label(self):
        for value, label in FitnessUser.Role.choices:
            if self.role == value:
                return label


