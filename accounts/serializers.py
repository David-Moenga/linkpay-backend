from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "name", "account_type", "phone", "business_name", "is_verified", "is_flagged", "roles", "date_joined")
        read_only_fields = ("id", "is_verified", "is_flagged", "date_joined")

    def get_name(self, user):
        return user.display_name

    def get_roles(self, user):
        roles = list(user.groups.values_list("name", flat=True))
        if not roles:
            roles = [user.account_type or "user"]
        return roles


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ("username", "email", "password", "account_type", "phone", "business_name", "first_name", "last_name")

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return email

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        email = validated_data["email"].lower()
        user = User.objects.create_user(username=validated_data["username"], email=email, password=password, **{k: v for k, v in validated_data.items() if k not in ("username", "email")})
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
