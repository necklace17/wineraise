"""Tests for the wine api endpoint."""
import statistics
import uuid
from decimal import Decimal
from statistics import mean
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from rest_framework import status
from core.test.basetestclasses import (
    PrivateAPITestCase,
    PublicAPITestCase,
    create_user,
)
from wine.models import Wine, Library, Tag, Review
from wine.serializers import (
    WineSerializer,
    LibrarySerializer,
    TagSerializer,
    ReviewSerializer,
)


# Store the wine list url as constant value
WINES_LIST_URL = reverse("wine:wine-list")


def get_wine_details_url(wine_id):
    """Get the wine detail url."""
    return reverse("wine:wine-detail", args=[wine_id])


def get_wine_add_review_url(wine_id):
    """Get the url to add a comment to the wine."""
    return reverse("wine:wine-add-review", args=[wine_id])


def create_sample_wine(name=None, user=None, **kwargs):
    """Create a sample wine."""
    if not name:
        # Create random name, if name is not given
        random_id = str(uuid.uuid1())[:8]
        name = "Sample wine " + random_id
    if not user:
        # Get the first user, if user is not given
        user = get_user_model().objects.first()
    points = kwargs.pop("points", None)
    # Create wine
    wine = Wine.objects.create(name=name, user=user, **kwargs)
    # If points are given, create a review with the given points
    if points:
        Review.objects.create(wine=wine, points=points, user=user)

    return wine


def create_sample_library(name=None, public=False, user=None, **kwargs):
    """Create sample library."""
    if not name:
        # If no name is given, generate a random unique name
        random_id = str(uuid.uuid1())[:8]
        name = "Sample library " + random_id
    if not user:
        # Get the first user, if user is not given
        user = get_user_model().objects.first()
    # Create the wine and return it
    return Library.objects.create(
        name=name, public=public, user=user, **kwargs
    )


def create_sample_tag(name=None, user=None, **kwargs):
    """Create sample tag."""
    if not name:
        # If no name is given, create a unique one
        random_id = str(uuid.uuid1())[:8]
        name = "Sample tag " + random_id
    if not user:
        # Get the first user, if user is not given
        user = get_user_model().objects.first()
    # Create the tag and return it
    return Tag.objects.create(name=name, user=user, **kwargs)


class TestPublicWineAPI(PublicAPITestCase):
    """Test for Public Wine API."""

    def test_wine_url(self):
        """Test the wine url."""
        # Access the tags url as unauthenticated user
        res = self.client.get(WINES_LIST_URL)
        # Assert an UNAUTHORIZED response
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateWineAPI(PrivateAPITestCase):
    """Tests for Private Wine App."""

    def create_login_other_user(self):
        """Helper function that create a user and logs in."""
        # Log in with different user
        self.user = create_user()
        # Authenticate as user
        self.client.force_authenticate(self.user)

    def test_wine_url(self):
        """Test the wine url."""
        # Access the wine url
        res = self.client.get(WINES_LIST_URL)
        # Assert a successful response
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_wine_creation(self):
        """Test the creation of a wine."""
        # Create payload
        payload = {
            "name": "Quinta dos Avidagos 2011 Avidagos Red (Douro)",
            "description": "This is a fruity  wine.",
            "price": Decimal("15.00"),
            "designation": "Avidagos",
            "variety": "Portuguese Red",
            "region_1": "Douro 1",
            "region_2": "Douro 2",
            "province": "Douro",
            "country": "Portugal",
            "winery": "Quinta dos Avidagos",
        }
        # Post the payload the wine url
        res = self.client.post(WINES_LIST_URL, payload, format="json")
        # Assert a successfully created response
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # Get all wines
        wines = Wine.objects.all()
        # Wine table should not be empty
        self.assertTrue(wines.exists())
        # Should be only 1 wine
        self.assertEqual(wines.count(), 1)
        # Get the wine
        wine = wines.first()
        # Check wine id
        self.assertEqual(wine.id, res.data["id"])
        # Check user is linked
        self.assertEqual(wine.user, self.user)
        # Check created_at not empty
        self.assertIsNotNone(wine.created_at)
        # Check all other attributes are created properly
        for key, value in payload.items():
            self.assertEqual(value, getattr(wine, key))

    def test_wine_list(self):
        """Test the wine list representation."""
        # Define number of wines to create
        number_of_wines = 2
        # Create 2 wines
        for __ in range(number_of_wines):
            create_sample_wine()
        wines = Wine.objects.all()

        # Create an login with other user
        self.create_login_other_user()
        # Go to wine url
        res = self.client.get(WINES_LIST_URL)
        # Check if all wines are listed
        serializer = WineSerializer(wines, many=True)
        # Check for equality
        self.assertEqual(res.data, serializer.data)

    def test_detail_view(self):
        """Test the detail view of wine."""
        # Create sample libraries and tags
        libraries = [create_sample_library() for __ in range(2)]
        tags = [create_sample_tag() for __ in range(2)]
        # Create sample wine
        wine = create_sample_wine()
        # Add libraries and tags to wine
        for library in libraries:
            wine.libraries.add(library)
        for tag in tags:
            wine.tags.add(tag)
        # Get the specific wine url
        url = get_wine_details_url(wine.id)
        # Access the wine ulr
        res = self.client.get(url)

        # Serialize the libraries and tags
        library_serializer = LibrarySerializer(libraries, many=True)
        tags_serializer = TagSerializer(tags, many=True)

        # Assert that both are in the response
        self.assertEqual(res.data["libraries"], library_serializer.data)
        self.assertEqual(res.data["tags"], tags_serializer.data)

    def test_add_review(self):
        """Test to add a review to a wine."""
        # Create sample wine
        wine = create_sample_wine()
        # Add user and login
        self.create_login_other_user()
        # Get wine url
        url = get_wine_add_review_url(wine.id)
        # Create review with comment
        first_points = 87
        payload = {
            "points": first_points,
            "comments": "This is a great wine.",
        }
        # Post the payload
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Create second review
        second_points = 50
        payload = {
            "points": second_points,
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Check that reviews have been created
        reviews = Review.objects.all()
        self.assertTrue(reviews.exists())
        # Check that both reviews are visible on the site
        serializer = ReviewSerializer(reviews, many=True)
        wine_details_url = get_wine_details_url(wine.id)
        res = self.client.get(wine_details_url)
        self.assertEqual(res.data["reviews"], serializer.data)
        # Check that the average of points is visible
        self.assertIn("point_average", res.data)
        # Check that the point average has been calculated correct
        wine.refresh_from_db()
        # Calculate the average by ourselves and compare it
        average = mean([first_points, second_points])
        self.assertEqual(average, wine.point_average)

    def test_invalid_review(self):
        """Test to create a review without points."""
        # Create sample wine
        wine = create_sample_wine()
        # Get specific wine url
        url = get_wine_add_review_url(wine.id)
        # Create invalid review without points
        payload = {
            "comments": "This is a great wine.",
        }
        # Post the payload to the specific wine url
        res = self.client.post(url, payload, format="json")
        # Assert a BAD REQUEST
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_with_wine_id(self):
        """Test to create a review without points."""
        # Create sample wine
        wine = create_sample_wine()
        # Get wine url
        url = get_wine_add_review_url(wine.id)
        # Create invalid review without points
        payload = {
            "wine_id": wine.id,
            "points": 87,
            "comments": "This is a great wine.",
        }
        # Post the payload to the specific wine url
        res = self.client.post(url, payload, format="json")
        # Assert a successful response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Assert that the reviews for the wine exists
        self.assertTrue(wine.reviews.exists())

    def test_add_wine_to_library(self):
        """Create a wine and add it to library."""
        # Create a library
        library = create_sample_library()
        # Creat a wine
        wine = create_sample_wine()
        # check that everything is from the same user
        self.assertEqual(self.user, wine.user, library.user)
        # Get the specific wines url
        url = get_wine_details_url(wine.id)
        # Generate a payload with the library id
        payload = {
            "libraries": [library.id],
        }
        # Use the http patch function to update the wine object
        res = self.client.patch(url, payload, format="json")
        # Assert a successful response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Assert that the library is now listed
        self.assertEqual(1, len(res.data["libraries"]))
        # Assert the correct id
        self.assertEqual(library.id, res.data["libraries"][0])
        # Test that also the wine is linked at the library
        library.refresh_from_db()
        self.assertIn(wine, library.wines.all())

    def test_add_wine_to_foreign_library(self):
        """Test to wine to a library from another user."""
        # Create another user
        other_user = create_user()
        # Create a library with this user
        other_users_library = create_sample_library(
            user=other_user, public=True
        )
        # Check that the library has been created as expected
        self.assertEqual(other_user, other_users_library.user)
        self.assertNotEqual(self.user, other_user)
        # create a wine
        wine = create_sample_wine()
        # Get the specific wine url
        url = get_wine_details_url(wine.id)
        # Create a payload with the library id
        payload = {
            "libraries": [other_users_library.id],
        }
        # Use the http patch method to modify the object
        res = self.client.patch(url, payload, format="json")
        # Assert a BAD REQUEST
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Assert that the library has not been added
        self.assertFalse(res.data.get("libraries"))

    def test_search_by_name(self):
        """Test to search for a wine by name."""
        # Create a wine with a specific name
        wine_name = "Franconian Wine"
        create_sample_wine(name=wine_name)
        # Create another wine with random different name
        create_sample_wine()
        # Get the wine list and use the name param as filter
        res = self.client.get(WINES_LIST_URL, {"name": wine_name})
        # Check that only one wine is returned
        self.assertEqual(1, len(res.data))
        # Assert that the correct one is returned
        self.assertEqual(res.data[0]["name"], wine_name)

    def test_search_by_price(self):
        """
        Test to search by price which is lower or higher than given value.
        """
        # Create low budget wine
        low_price = Decimal("5.00")
        low_budget_wine = create_sample_wine(**{"price": low_price})
        # Create high budget wine
        high_price = Decimal("12.00")
        high_budget_wine = create_sample_wine(**{"price": high_price})
        mean_price = statistics.mean([low_price, high_price])
        # Filter for low budget wines
        res = self.client.get(WINES_LIST_URL, {"max_price": mean_price})
        self.assertEqual(1, len(res.data))
        self.assertEqual(res.data[0]["name"], low_budget_wine.name)
        # Filter for high budget wines
        res = self.client.get(WINES_LIST_URL, {"min_price": mean_price})
        self.assertEqual(1, len(res.data))
        self.assertEqual(res.data[0]["name"], high_budget_wine.name)
        # Get no wine
        res = self.client.get(WINES_LIST_URL, {"price": mean_price})
        self.assertFalse(res.data)
        # Get exactly the low budget wine
        res = self.client.get(WINES_LIST_URL, {"price": low_price})
        self.assertEqual(1, len(res.data))
        self.assertEqual(res.data[0]["name"], low_budget_wine.name)
        # Grate an out of range wine and low low budget wine
        for price in [Decimal("120.00"), Decimal("2.00")]:
            create_sample_wine(**{"price": price})
        # Test to filter with two parameters
        res = self.client.get(
            WINES_LIST_URL,
            {
                "min_price": low_price,
                "max_price": high_price,
            },
        )
        # Assert the correct number
        self.assertEqual(2, len(res.data))
        # Serialize the wines
        serializer = WineSerializer(
            [low_budget_wine, high_budget_wine], many=True
        )
        # Assert the correct data
        self.assertEqual(serializer.data, res.data)

    def test_search_by_review_points(self):
        """Test to search by review points."""
        # Create low rated wine
        low_points = 20
        low_rated_wine = create_sample_wine(points=low_points)
        # Create high rated wine
        high_points = 90
        high_rated_wine = create_sample_wine(points=high_points)
        mean_points = statistics.mean([low_points, high_points])
        # Filter for high rated wines
        res = self.client.get(
            WINES_LIST_URL, {"min_point_average": mean_points}
        )
        self.assertEqual(1, len(res.data))
        serializer = WineSerializer(high_rated_wine)
        self.assertEqual(serializer.data, res.data[0])
        # Filter for low rated wines
        res = self.client.get(
            WINES_LIST_URL, {"max_point_average": mean_points}
        )
        # Assert the correct length
        self.assertEqual(1, len(res.data))
        # Serializer the wine
        serializer = WineSerializer(low_rated_wine)
        # Assert that this structure is visible
        self.assertEqual(serializer.data, res.data[0])
