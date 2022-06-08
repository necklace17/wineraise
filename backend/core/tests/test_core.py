"""Test the functionalities of the core app"""
from django.urls import reverse
from rest_framework import status

from core.test.basetestclasses import PublicAPITestCase

# Store open api url as constant value
OPENAPI_URL = reverse("openapi-schema")
# Store swagger url as constant value
SWAGGER_URL = reverse("swagger-ui")


class TestDocumentationSites(PublicAPITestCase):
    """Test the API documentation sites."""

    def test_swagger_ui_site(self):
        """Test the swagger site."""
        # Access the url
        res = self.client.get(SWAGGER_URL)
        # Check the status code
        self.assertTrue(res.status_code, status.HTTP_200_OK)

    def test_openapi_site(self):
        """Test the OpenAPI site"""
        # Access the url
        res = self.client.get(OPENAPI_URL)
        # Check the status code
        self.assertTrue(res.status_code, status.HTTP_200_OK)
