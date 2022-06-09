"""Models for wine app."""
from django.core import validators
from django.db import models
from django.conf import settings
from decimal import Decimal

from django.db.models import Avg


class BaseModelWineAppModel(models.Model):
    """
    Abstract Base Wine App Model.

    The model provides the user related fields 'user' which links to the user.
    'created_at' which is the date, the object is created and 'updated_at'
    which is the date time field which describes the last update of the object.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta data.

        Defines that this model is abstract and just used as a template at
        other models. This abstract model is not replicated in the database.
        """

        abstract = True


class Library(BaseModelWineAppModel):
    """Model for Wine Library to collect multiple wines."""

    name = models.CharField(max_length=125)
    description = models.CharField(max_length=1000, null=True)
    public = models.BooleanField(default=False)

    def __str__(self):
        """Represent as string."""
        return self.name


class Tag(BaseModelWineAppModel):
    """
    Tag for Wine to tag wines i.e. with specific flavor or characteristic.
    """

    name = models.CharField(max_length=125)

    def __str__(self):
        """Represent as string."""
        return self.name


class Review(BaseModelWineAppModel):
    """Model for review.

    A review is related to a specific wine. The review has points which is a
    necessary field an comments which is optional.
    """

    wine = models.ForeignKey(
        "Wine", on_delete=models.CASCADE, related_name="reviews"
    )
    points = models.PositiveSmallIntegerField(
        validators=[validators.MaxValueValidator(100)]
    )
    comment = models.CharField(max_length=1000, null=True)

    def __str__(self):
        """Represent string."""
        if self.comment:
            return '{} - {} Points: "{}" from {}'.format(
                str(self.wine), str(self.points), self.comment, str(self.user)
            )
        return "{} - {} Points from {}".format(
            str(self.wine), str(self.points), str(self.user)
        )


class Wine(BaseModelWineAppModel):
    """Model for Wine."""

    libraries = models.ManyToManyField("Library", related_name="wines")
    tags = models.ManyToManyField("Tag", related_name="wines")

    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=1000, null=True)
    price = models.DecimalField(
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(1000000),
        ],
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
    )
    designation = models.CharField(max_length=255, null=True, blank=True)
    variety = models.CharField(max_length=255, null=True, blank=True)
    region_1 = models.CharField(max_length=255, null=True, blank=True)
    region_2 = models.CharField(max_length=255, null=True, blank=True)
    province = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    winery = models.CharField(max_length=255, null=True, blank=True)

    @property
    def point_average(self) -> Decimal:
        """Return average of points."""
        if self.reviews.exists():
            return Decimal(
                self.reviews.aggregate(average=Avg("points"))["average"]
            )
        return Decimal("0")

    def __str__(self):
        """Represent as string."""
        return self.name
