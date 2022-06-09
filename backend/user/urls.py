"""Configuration and declaration of app specific urls for the user app."""
from django.urls import path
from user import views as user_views

# Set the app name
app_name = "user"

urlpatterns = [
    # Create url to create an user
    path("create/", user_views.CreateUserView.as_view(), name="create"),
    # Token url to generate an token
    path("token/", user_views.CreateTokenView.as_view(), name="token"),
    # Me url to view user information
    path("me/", user_views.ManageUserView.as_view(), name="me"),
]
