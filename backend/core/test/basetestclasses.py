"""
To achieve a quicker testing, this module provides some base test classes as
well as helper functions for further test cases.
"""
import uuid
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient


def create_user(**kwargs):
    """
    Help to create a user.

    If now keyword arguments are passed, a standard user will be created.
    """
    if not kwargs.get("email"):
        # No param for email is provided
        # Generate random id to use in the email (needed when multiple users
        # are created)
        random_id = str(uuid.uuid1())[:8]
        # Generate email
        kwargs["email"] = f"wine_lover.{random_id}@aol.com"
    # Generate user data
    user_data = {
        "email": kwargs["email"],
        "name": kwargs.get("email", "John Doe"),
    }
    # Create the user
    user = get_user_model().objects.create(**user_data)
    # Set the given or a sample password
    user.set_password(kwargs.get("password", "standardpassword"))
    # Save the user and return the instance
    user.save()

    return user


class APIBaseTestCase(TestCase):
    """API Base Test Class."""

    def setUp(self) -> None:
        """Setup class with API Client."""
        self.client = APIClient()


class PublicAPITestCase(APIBaseTestCase):
    """Base Test class for public api."""


class PrivateAPITestCase(APIBaseTestCase):
    """
    Base Test class for Private API.

    The class generates a user and logs in to access private endpoints.
    """

    def setUp(self) -> None:
        """Setup class with logged in user."""
        super().setUp()
        # Create user
        self.user = create_user(
            **{
                "email": "greates.winelover@aol.com",
                "name": "John Doe the first.",
                "password": "testpass",
            }
        )
        # Log in with the user
        self.client.force_authenticate(self.user)
