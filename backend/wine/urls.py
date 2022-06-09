"""Configuration and declaration of app specific urls for the wine app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from wine import views

# Declare an router
router = DefaultRouter()
# Register the wine view set at the router
router.register("wines", viewset=views.WineViewSet)
# Register the library view set at the router
router.register("libraries", viewset=views.LibraryViewSet)
# Register the tags view set at the router
router.register("tags", viewset=views.TagViewSet)


app_name = "wine"

# Add the router urls to the url patterns
urlpatterns = [path("", include(router.urls))]
