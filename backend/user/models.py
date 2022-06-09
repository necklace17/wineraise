"""Models for the user app.

The models represent the database model at object level.
"""
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Custom User Manager Class."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a new User."""
        if not email:
            # Mail needs to be provided. It is used as the unique user name
            raise ValueError("User must have an email address")
        # Create the user
        user = self.model(email=self.normalize_email(email), **extra_fields)
        # Use the set password function to store the hash value of the password
        user.set_password(password)
        # Save the user instance
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and save a new super user."""
        # first, use the normal create user function
        user = self.create_user(email, password)
        # Set is staff to true
        user.is_staff = True
        # Set is superuser to true
        user.is_superuser = True
        # Save the user instance
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    objects = UserManager()
    USERNAME_FIELD = "email"
