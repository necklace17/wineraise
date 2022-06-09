"""Tests for the tags api endpoint."""

from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from core.test.basetestclasses import PublicAPITestCase, PrivateAPITestCase
from wine.models import Tag, Wine
from wine.serializers import TagSerializer


# Store the tags url as a constant value
TAGS_URL = reverse("wine:tag-list")


class PublicTagsApiTests(PublicAPITestCase):
    """Test the publicly available tags API"""

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        # Access the tags url as unauthenticated user
        res = self.client.get(TAGS_URL)
        # Assert an UNAUTHORIZED response
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(PrivateAPITestCase):
    """Test the private tags api endpoint."""

    def test_tags_url(self):
        """Test the tags list url."""
        # Create 2 tags
        Tag.objects.create(user=self.user, name="Fruity")
        Tag.objects.create(user=self.user, name="Not Fruity")
        # Access the tags site
        res = self.client.get(TAGS_URL)
        # Assert successful response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Get all Tag objects and order reverse by name
        tags = Tag.objects.all().order_by("-name")
        # Serialize them
        serializer = TagSerializer(tags, many=True)
        # Assert that this is the response
        self.assertEqual(res.data, serializer.data)

    def test_create_tag_successfully(self):
        """Test creating a new tag."""
        # Generate payload
        payload = {
            "name": "My New Tag",
        }
        # Post the payload to the tags url
        res = self.client.post(TAGS_URL, payload, format="json")
        # Assert a successfully created response
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # Assert that the tag has been created in the databse
        exists = (
            Tag.objects.all()
            .filter(user=self.user, name=payload["name"])
            .exists()
        )
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating an new tag with invalid payload."""
        # Generate an invalid payload (tag without name)
        payload = {
            "name": "",
        }
        # Post the payload to the tags url
        res = self.client.post(TAGS_URL, payload, format="json")
        # Assert a bad request as response
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_wines(self):
        """Test filtering tags by those assigned to wines."""
        # Create two tags
        tag1 = Tag.objects.create(user=self.user, name="Fruity")
        tag2 = Tag.objects.create(user=self.user, name="Not Fruity")
        # Create a wine
        wine = Wine.objects.create(
            name="Quinta dos Avidagos 2011 Avidagos Red (Douro)",
            description="This is a fruity  wine.",
            price=Decimal("15.00"),
            user=self.user,
        )
        # Add the first tag to the wine
        wine.tags.add(tag1)
        # Save the wine
        wine.save()
        # Access tags url and pass the assigned tags only parameter
        res = self.client.get(TAGS_URL, {"assigned_only": 1})
        # Serialize both tags
        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        # Test that the first tag is part of the response...
        self.assertIn(serializer1.data, res.data)
        # ... and the second not
        self.assertNotIn(serializer2.data, res.data)
