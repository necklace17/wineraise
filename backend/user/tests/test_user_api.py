"""Test file for the user endpoints."""
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from rest_framework import status

from core.test.basetestclasses import (
    PublicAPITestCase,
    create_user,
    PrivateAPITestCase,
)

# Get the create user url as a constant value
CREATE_USER_URL = reverse("user:create")
# Get the token url as a constant value
TOKEN_URL = reverse("user:token")
# Get the me url as a constant value
ME_URL = reverse("user:me")


class TestPrivateUserAPI(PrivateAPITestCase):
    """Test the private user api endpoint."""

    def test_retrieve_user_authorized(self):
        """Test that authentication is required for the me url."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestPublicUserAPI(PublicAPITestCase):
    """Test Private User API."""

    def test_create_valid_user_success(self):
        """Test the user creation process."""
        # Generate payload
        payload = {
            "email": "ilikewine@wine.de",
            "password": "test_password",
            "name": "Ned Stark",
        }
        # Post the payload
        res = self.client.post(CREATE_USER_URL, payload, format="json")
        # Test the response status code
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # Get the generated user
        user = get_user_model().objects.get(**res.data)
        # check that the password has been created properly
        self.assertTrue(user.check_password(payload["password"]))
        # Check that the generated password is not part of the response
        self.assertNotIn("password", res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails."""
        # Generate payload
        payload = {
            "email": "ilikewine@wine.de",
            "password": "testpass",
        }
        # Create the user with use of the helper function
        create_user(**payload)
        # Post the payload to try to create the user with the same data again
        res = self.client.post(CREATE_USER_URL, payload, format="json")
        # Assert 400 BAD REQUEST response
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters."""
        # Generate payload
        payload = {
            "email": "ilikewine@wine.de",
            "password": "pw",  # just 2 letters
            "name": "Test",
        }
        # Post the payload
        res = self.client.post(CREATE_USER_URL, payload, format="json")
        # Assert 400 BAD REQUEST response
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Filter for the user
        user_exists = (
            get_user_model().objects.filter(email=payload["email"]).exists()
        )
        # Assert that the query is empty
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user."""
        # Generate payload
        payload = {
            "email": "ilikewine@wine.de",
            "password": "testpass",
        }
        # Create the user
        user = create_user(**payload)
        # Assert that the user is active by default
        self.assertTrue(user.is_active)
        # Access the token url
        res = self.client.post(TOKEN_URL, payload, format="json")
        # Assert that the access is successful
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Assert that the token is in the response data
        self.assertIn("token", res.data)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given."""
        # Create user
        create_user(email="ilikewine@wine.de", password="testpass")
        # Generate payload with different password
        payload = {
            "email": "ilikewine@wine.de",
            "password": "wrong",
        }
        # Try to access the token page
        res = self.client.post(TOKEN_URL, payload, format="json")
        # Check that the response code is BAD REQUEST
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Check that the token is not available in the response
        self.assertNotIn("token", res.data)

    def test_create_token_no_user(self):
        """Test to create a token as a user that does not exists."""
        # Generate payload for a non existing user
        payload = {
            "email": "ilikewine@wine.de",
            "password": "testpass",
        }
        # Post the payload to the generate token page
        res = self.client.post(TOKEN_URL, payload, format="json")
        # Check that the response code is BAD REQUEST
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Check that the token is not available in the response
        self.assertNotIn("token", res.data)

    def test_create_token_missing_field(self):
        """
        Test that email and password are required at the generate token site.
        """
        # Generate payload with invalid email and invalid password
        payload = {
            "email": "one",
            "password": "",
        }
        # Post the payload to the generate token url
        res = self.client.post(TOKEN_URL, payload, format="json")
        # Check that the response code is BAD REQUEST
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Check that the token is not available in the response
        self.assertNotIn("token", res.data)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users."""
        # Try to access the me site
        res = self.client.get(ME_URL)
        # Assert that the response is UNAUTHORIZED
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
