from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import ProfileSerializer


class ProfileView(generics.GenericAPIView):
    """
    Retrieve or update the authenticated user's profile.
    """

    serializer_class = ProfileSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            request.user.profile
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            request.user.profile,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )