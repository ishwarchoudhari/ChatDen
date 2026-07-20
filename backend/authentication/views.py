# Create your views here.
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer
from rest_framework_simplejwt.exceptions import (
    InvalidToken,
    TokenError,
)

from .serializers import (
    LoginSerializer,
    RefreshSerializer,
    LogoutSerializer,
    UserSerializer,
)


class LoginView(generics.GenericAPIView):
    """
    Authenticate a user and issue JWT access and refresh tokens.
    """

    serializer_class = LoginSerializer

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        """
        Authenticate user credentials and return JWT tokens.
        """

        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(
            raise_exception=True,
        )

        user = serializer.validated_data["authenticated_user"]

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )

class RefreshView(generics.GenericAPIView):
    """
    Refresh JWT access and refresh tokens.
    """

    serializer_class = RefreshSerializer

    authentication_classes = []

    permission_classes = [AllowAny]

    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )

        try:
            serializer.is_valid(
                raise_exception=True,
            )

        except (TokenError, InvalidToken):

            return Response(
                {
                    "detail": "Invalid or expired refresh token.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = {
            "access": serializer.validated_data["access"],
        }

        if "refresh" in serializer.validated_data:
            response["refresh"] = serializer.validated_data["refresh"]

        return Response(
            response,
            status=status.HTTP_200_OK,
        )
    
class LogoutView(generics.GenericAPIView):
    """
    Blacklist a refresh token.
    """

    serializer_class = LogoutSerializer

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "detail": "Successfully logged out."
            },
            status=status.HTTP_200_OK,
        )    
    
class MeView(generics.GenericAPIView):
    """
    Return the authenticated user's details.
    """

    serializer_class = UserSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            request.user
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )    