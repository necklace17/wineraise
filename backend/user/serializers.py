"""
Serializers for the user app.

"""
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        """Class Meta settings"""

        # Use the user model
        model = get_user_model()
        # Use the following fields
        fields = (
            "email",
            "password",
            "name",
        )
        # Pass further settings
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it."""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            # If a password is provided, use the set password function
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """
    Serializer for the token which will be used by the user for further
    authentication."""

    # email and passwords are needed
    email = serializers.CharField(label="Email")
    password = serializers.CharField(
        label="Password",
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validated the user input."""
        # Get the email and password
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            # If both are provided, authenticate the user
            user = authenticate(
                request=self.context.get("request"),
                email=email,
                password=password,
            )

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                # If no user is found, the function was not able to
                # authenticate
                # Generate a message
                msg = "Unable to log in with provided credentials."
                # Return the message with a validation error
                raise serializers.ValidationError(msg, code="authorization")
        else:
            # If no password and mail are provided...
            # Generate a proper message and raise a validation error
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code="authorization")

        # If success, set the user as attribute and return the attributes
        attrs["user"] = user
        return attrs
