"""Serializers for wine app."""
from collections import OrderedDict

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from wine.models import Wine, Tag, Library, Review


class LibrarySerializer(serializers.ModelSerializer):
    """Serializer for Library Object."""

    wines = serializers.PrimaryKeyRelatedField(
        many=True, required=False, queryset=Wine.objects.all()
    )

    class Meta:
        """Class Meta"""

        model = Library
        fields = (
            "id",
            "name",
            "description",
            "public",
            "wines",
            "created_at",
        )
        read_only_fields = ("id",)


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag Object."""

    class Meta:
        """Class Meta"""

        model = Tag
        exclude = ("user",)
        read_only_fields = ("id",)


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for review object.

    It is used to add a review to a wine and view it.
    """

    comment = serializers.CharField(required=False)

    class Meta:
        """Class Meta"""

        model = Review
        exclude = ("user",)
        read_only_fields = ("id",)


class WineSerializer(serializers.ModelSerializer):
    """Serializer for Wine Object."""

    libraries = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Library.objects.all(), required=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=False
    )
    reviews = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Review.objects.all(), required=False
    )

    def validate(self, attrs):
        """
        Validate that the attrs of libraries have the same user as the wine.
        """
        if attrs.get("libraries"):
            if any(
                [
                    library.user != self.instance.user
                    for library in attrs["libraries"]
                ]
            ):
                raise ValidationError("Can not add library.")

        return attrs

    class Meta:
        """Class Meta."""

        model = Wine
        fields = (
            "id",
            "libraries",
            "tags",
            "reviews",
            "point_average",
            "name",
            "description",
            "price",
            "designation",
            "variety",
            "region_1",
            "region_2",
            "province",
            "country",
            "winery",
        )
        read_only_fields = ("id",)

    def to_representation(self, instance):
        """
        Represents the model.

        If a value is none, it will not be shown in the representation.
        """
        result = super().to_representation(instance)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None]
        )


class WineDetailSerializer(WineSerializer):
    """
    Serializes a Wine object in detail.

    This serializer is inherited from the other Wine Serializer.
    """

    libraries = LibrarySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
