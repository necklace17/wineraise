"""Tests for the library endpoint."""
from django.urls import reverse
from rest_framework import status

from core.test.basetestclasses import (
    PublicAPITestCase,
    PrivateAPITestCase,
    create_user,
)
from wine.models import Library
from wine.serializers import LibrarySerializer
from wine.tests.test_wine_api import create_sample_library, create_sample_wine


# Store the library list url as a constant value
LIBRARY_URL = reverse("wine:library-list")


def get_library_details_url(library_id=None):
    """Get the library details url."""
    return reverse("wine:library-detail", args=[library_id])


class PublicLibraryApiTests(PublicAPITestCase):
    """Test the publicly available tags API."""

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        # Access the library url unauthenticated
        res = self.client.get(LIBRARY_URL)
        # Assert a UNAUTHORIZED response
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateLibraryApiTests(PrivateAPITestCase):
    """Test the private library api endpoint."""

    def test_library_creation(self):
        """Test the creation of a wine library."""
        # Generate payload
        payload = {
            "name": "The best wines",
            "description": "Here i will only save the best wines.",
        }
        # Create the library
        res = self.client.post(LIBRARY_URL, payload, format="json")
        # Assert an 201 Created response
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # Check that the library has been created
        libraries = Library.objects.all()
        self.assertTrue(libraries.exists())
        library = libraries.first()
        # serialize the library instance
        serializer = LibrarySerializer(library)
        # Check that the given payload has been created
        for key, value in payload.items():
            self.assertEqual(payload[key], serializer.data[key])
        # Check that by default, the library is private
        self.assertFalse(serializer.data["public"])
        # Check that the date has been saved
        self.assertIsNotNone(serializer["created_at"])
        # Check that the user which has created the library is linked
        self.assertEqual(library.user, self.user)

    def test_create_library_without_description(self):
        """
        Test to create a library without description.

        This should not end in an error.
        """
        # Generate payload without description
        payload = {
            "name": "Great library",
        }
        # Post the payload the the library url
        res = self.client.post(LIBRARY_URL, payload, format="json")
        # Assert that the library can be created
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        libraries = Library.objects.all()
        self.assertTrue(libraries.exists())
        library = libraries.first()
        # Check that the name has been created properly
        self.assertEqual(library.name, payload["name"])
        # Check that description is empty
        self.assertFalse(library.description)

    def test_create_library_without_name(self):
        """Test to create a library without a name.

        This should end in an error.
        """
        # Generate payload
        payload = {
            "description": "So much to tell here, no idea for a name",
        }
        # Post the payload to the library url
        res = self.client.post(LIBRARY_URL, payload, format="json")
        # Assert that the actions returns a BAD REQUEST
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Assert that not library exists
        libraries_exists = Library.objects.all().exists()
        self.assertFalse(libraries_exists)

    def test_private_library_not_visible(self):
        """Create private library, check it is not visible for others."""
        # Create library
        library = create_sample_library()
        # Check that library is not public
        self.assertFalse(library.public)
        # Check that the library has been created by the current user
        self.assertEqual(library.user, self.user)
        # Access the library url
        res = self.client.get(LIBRARY_URL)
        # Assert a successful response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Check that the data is there
        self.assertIsNotNone(res.data)
        # Create other user
        self.user = create_user()
        # Authenticate with the user
        self.client.force_authenticate(self.user)
        # Access the library url
        res = self.client.get(LIBRARY_URL)
        # Assert a successful response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # But assert that not data is shown
        self.assertFalse(res.data)

    def test_public_library_visible(self):
        """Create public library, check it is visible for others."""
        # Create public library
        library = create_sample_library(public=True)
        # Assert that the library has been created public
        self.assertTrue(library.public)
        # Assert that the creator is the current user
        self.assertEqual(library.user, self.user)
        # Access the library url
        res = self.client.get(LIBRARY_URL)
        # Assert a successful response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Assert that data is shown
        self.assertIsNotNone(res.data)
        # Create another user
        self.user = create_user()
        # Authenticate as the user
        self.client.force_authenticate(self.user)
        # Access the library url
        res = self.client.get(LIBRARY_URL)
        # Assert a successful response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Assert that data is shown
        self.assertIsNotNone(res.data)

    def test_only_mine_param(self):
        """Test to filter the libraries only for mine."""
        # Create a public library as first user
        create_sample_library(public=True)
        # Create a new user and set as the current user
        self.user = create_user()
        # Authenticate with the user
        self.client.force_authenticate(self.user)
        # Creat a library as the user
        second_library = create_sample_library(user=self.user)
        # Check that the library was properly created by the current user
        self.assertEqual(self.user, second_library.user)
        # Access the library url
        res = self.client.get(LIBRARY_URL)
        # Assert a successful response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Check that both libraries are visible
        self.assertEqual(2, len(res.data))
        # Check no with param that only my library is visible
        res = self.client.get(
            LIBRARY_URL,
            {
                "only_mine": "1",
            },
        )
        # Assert a successful response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Check that both libraries are visible
        self.assertEqual(1, len(res.data))

    def test_wine_in_library(self):
        """Test to see if the wines are visible at the library api."""
        # Create a library
        library = create_sample_library()
        # Create a wine
        wine = create_sample_wine()
        # Assign the wine to the library
        library.wines.add(wine)
        # Save the library
        library.save()
        # Get the library url
        url = get_library_details_url(library.id)
        # Access the library url
        res = self.client.get(url)
        # Assert a successful response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Assert that the wines are in the library
        self.assertIn("wines", res.data)
        # Assert that the correct wine library is in the response
        self.assertIn(library.id, res.data["wines"])

    def test_add_wine_to_library(self):
        """Test to add a wine to library."""
        # Create a library
        library = create_sample_library()
        # Create a first wine
        first_wine = create_sample_wine()
        # Create a second wine
        second_wine = create_sample_wine()
        # Get the url of the library
        url = get_library_details_url(library.id)
        # Generate a payload with the two wines
        payload = {
            "wines": [
                first_wine.id,
                second_wine.id,
            ]
        }
        # Use the http patch method to change the wine
        res = self.client.patch(url, payload, format="json")
        # Assert a successful response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Assert that both wines are in the response
        self.assertEqual(res.data["wines"], [first_wine.id, second_wine.id])
        # Refresh the library instance from the db
        library.refresh_from_db()
        # Assert that the wines are also stored properly in the database
        self.assertEqual([first_wine, second_wine], list(library.wines.all()))
