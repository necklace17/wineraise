"""Views for the wine app."""
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from wine.filters import WineFilter
from wine.models import Wine, Library, Tag
from wine import serializers


class BaseWineAppViewSet(viewsets.ModelViewSet):
    """Base View set for wine app."""

    # Permission Classes
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Workaround for django filters UserWarning."""
        if self.request is None:
            return
        return super().get_queryset()

    def perform_create(self, serializer):
        """Perform the creation of a wine and link the current user."""
        serializer.save(user=self.request.user)


class LibraryViewSet(BaseWineAppViewSet):
    """View Set for Library."""

    serializer_class = serializers.LibrarySerializer
    queryset = Library.objects.all()
    filterset_fields = (
        "name",
        "description",
    )

    def get_queryset(self):
        """
        Get the queryset.

        All private libraries are filtered out by default.
        Also it is possible to search only for own libraries.
        """
        if self.request is None:
            # Workaround for django filter user warning
            return self.get_serializer_class().Meta.model.objects.none()
        # Get the queryset
        queryset = super().get_queryset()
        # Check for the only_mine param
        only_mine = bool(int(self.request.query_params.get("only_mine", 0)))
        if only_mine:
            # If the param is given, get only my libraries
            queryset = queryset.filter(user=self.request.user)
        else:
            # If not, get all visible libraries (mine and all other public)
            queryset = queryset.filter(
                Q(user=self.request.user) | Q(public=True)
            )
        return queryset


class TagViewSet(BaseWineAppViewSet):
    """View Set for Tags."""

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all().order_by("-name")
    filterset_fields = ("name",)

    def get_queryset(self):
        """
        Return the queryset.

        User can filter if he just wants to receive the assigned tags.
        """
        if self.request is None:
            # Workaround for django filter user warning
            return self.get_serializer_class().Meta.model.objects.none()

        queryset = super().get_queryset()
        # Check for the assigned only param
        assigned_only = bool(
            int(self.request.query_params.get("assigned_only", 0))
        )
        if assigned_only:
            # If the param is given, filter for only assigned tags
            queryset = queryset.filter(wines__isnull=False)

        return queryset


class WineViewSet(BaseWineAppViewSet):
    """View set for Wine."""

    serializer_class = serializers.WineSerializer
    queryset = Wine.objects.all()

    filterset_class = WineFilter

    def get_serializer_class(self):
        """Get the appropriate serializer class."""
        if self.action == "retrieve":
            # If the action is retrieve, get the detail wine serializer
            return serializers.WineDetailSerializer
        elif self.action == "add_review":
            # If the action is "add_review", use the Review serializer
            return serializers.ReviewSerializer
        # If nothing of those actions are done, use the default serializer
        return self.serializer_class

    @action(methods=["POST"], detail=True, url_path="add-review")
    def add_review(self, request, pk=None):
        """Add review to a wine."""
        # Get the wine object
        wine = self.get_object()
        # Make the query_dict mutable
        query_dict = request.data.copy()
        # Add the wine id
        query_dict["wine"] = wine.id
        # Add to the serializer
        serializer = self.get_serializer(data=query_dict)
        if serializer.is_valid():
            # If the serializer is valid, save it and link the current user
            serializer.save(user=self.request.user)
            # Return a successful response and the data
            return Response(serializer.data, status=status.HTTP_200_OK)
        # If the serializer is not valid, return the error and BAD REQUEST
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
