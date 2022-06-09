"""File for defining multiple filters for the views."""
from django.db.models import Avg
from django_filters import rest_framework as filters
from wine.models import Wine


class WineFilter(filters.FilterSet):
    """Filterset for wines.."""

    # price filters
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")

    # point_average filters
    min_point_average = filters.NumberFilter(method="filter_min_point_average")
    max_point_average = filters.NumberFilter(method="filter_max_point_average")

    class Meta:
        """
        Meta Data.

        Defines the model as well as the used fields.
        """

        model = Wine
        fields = [
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
            "min_price",
            "max_price",
            "min_point_average",
            "max_point_average",
        ]

    @staticmethod
    def annotate_point_average(queryset):
        """
        Annotate the queryset for point average.

        field has the name annotation_point_average, since point_average
        already taken by property field.
        """
        return queryset.annotate(
            annotation_point_average=Avg("reviews__points")
        )

    def filter_min_point_average(self, queryset, name, value):
        """Filter for minimum point average."""
        queryset = self.annotate_point_average(queryset)
        return queryset.filter(annotation_point_average__gte=value)

    def filter_max_point_average(self, queryset, name, value):
        """Filter for maximum point average."""
        queryset = self.annotate_point_average(queryset)
        return queryset.filter(annotation_point_average__lte=value)
