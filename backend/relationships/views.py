"""
relationships/views.py

Views for the Blocking API.

Endpoints:
    GET    /api/v1/relationships/blocks/        -> list users I've blocked
    POST   /api/v1/relationships/blocks/        -> block a user
    DELETE /api/v1/relationships/blocks/<id>/   -> unblock a user

Responsibilities:
    - Enforce authentication (every endpoint requires a valid JWT).
    - Enforce OWNERSHIP: a user can only see/delete their OWN Block rows,
      never anyone else's. This is done via get_queryset(), not just
      permission_classes — IsAuthenticated only proves *someone* is
      logged in, not that they own the specific row being touched.
    - Enforce business rules (no self-block, no duplicate block) that
      BlockCreateSerializer deliberately leaves to this layer.
    - Delegate response shaping to BlockSerializer.

Does NOT:
    - Implement relationship policy logic — that's relationships/services.py.
    - Touch messaging, conversations, or anything outside blocking itself.
"""

# Django
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404

# DRF
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

# Local apps
from accounts.models import User

from .models import Block
from .serializers import (
    BlockCreateSerializer,
    BlockSerializer,
    PublicUserSerializer,
)
from .services import can_view_profile

class BlockListCreateView(generics.ListCreateAPIView):
    """
    GET  -> list of users the authenticated user has blocked.
    POST -> block a user by id.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        """
        CRITICAL: scoped to the current user's own outgoing blocks only.

        Without this filter, this endpoint would expose every block
        relationship on the entire platform to any authenticated user.
        """
        return (
            Block.objects.filter(blocker=self.request.user)
            .select_related("blocked")
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        # Input (POST) and output (GET) intentionally use different
        # serializers — see each serializer's own docstring for why.
        if self.request.method == "POST":
            return BlockCreateSerializer
        return BlockSerializer

    def create(self, request, *args, **kwargs):
        # BlockCreateSerializer only validates *structure* — does the id
        # resolve to a real user? Business rules live here, not in the
        # serializer, matching the separation of concerns it documents.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target_user = serializer.validated_data["user"]

        # Rule 1 — no self-block.
        # The model's CheckConstraint enforces this at the DB level too;
        # this check exists purely so the failure is a clean 400 with a
        # helpful message, instead of a raw IntegrityError turning into
        # an unhandled 500.
        if target_user.id == request.user.id:
            return Response(
                {"detail": "You cannot block yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Rule 2 — no duplicate block.
        # Same reasoning: the UniqueConstraint is the real guarantee,
        # this just makes the common-case failure friendly.
        already_blocked = Block.objects.filter(
            blocker=request.user, blocked=target_user
        ).exists()
        if already_blocked:
            return Response(
                {"detail": "You have already blocked this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            block = Block.objects.create(blocker=request.user, blocked=target_user)
        except IntegrityError:
            # Backstop for a race condition: two identical requests landing
            # at nearly the same instant could both pass the .exists()
            # check above before either has committed. The DB constraint
            # is the actual guarantee against a duplicate row ever being
            # created — this just keeps the HTTP response clean if that
            # narrow race happens.
            return Response(
                {"detail": "You have already blocked this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = BlockSerializer(
            block
            ,context=self.get_serializer_context()
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class BlockDeleteView(generics.DestroyAPIView):
    """
    DELETE -> unblock a user (removes the Block row).
    """

    permission_classes = [IsAuthenticated]
    serializer_class = BlockSerializer
    lookup_field = "id"

    def get_queryset(self):
        """
        CRITICAL: scoped to blocks the current user created.

        Without this filter, any authenticated user could pass any
        Block's UUID here and delete a relationship that isn't theirs —
        an IDOR vulnerability, silently un-blocking someone on another
        user's behalf.
        """
        return Block.objects.filter(blocker=self.request.user)
    
class UserSearchView(generics.GenericAPIView):
    """
    Search for public users by username.

    Endpoint
    --------
    GET /api/v1/relationships/search/?q=<search_term>

    Purpose
    -------
    Allows authenticated users to discover other users on the platform.

    Phase 4 Rules
    -------------
    - Authentication required.
    - Search by username only.
    - Minimum query length enforced.
    - Exclude the requesting user.
    - Exclude inactive users.
    - Exclude users involved in a block relationship.
    - Load Profile efficiently using select_related().
    - Return paginated results.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    serializer_class = PublicUserSerializer

    # Locked Phase 4 architecture:
    # Prevent extremely broad searches such as "a", "ab", or empty strings.
    MIN_SEARCH_QUERY_LENGTH = 3

    def get_queryset(self):
        """
        Build the discovery queryset.

        The queryset intentionally performs filtering at the database level
        rather than checking each user individually. This avoids N+1 queries
        and keeps discovery efficient.
        """

        blocked_user_ids = Block.objects.filter(
            Q(blocker=self.request.user) | Q(blocked=self.request.user)
        ).values_list("blocker_id", "blocked_id")

        excluded_ids = {self.request.user.id}

        for blocker_id, blocked_id in blocked_user_ids:
            excluded_ids.add(blocker_id)
            excluded_ids.add(blocked_id)

        return (
            User.objects.filter(is_active=True)
            .exclude(id__in=excluded_ids)
            .select_related("profile")
            .order_by("username")
        )

    def get(self, request, *args, **kwargs):
        """
        Execute a username search.

        Query Parameter
        ---------------
        q=<username>

        Example
        -------
        /search/?q=john
        """

        query = request.query_params.get("q", "").strip()

        if len(query) < self.MIN_SEARCH_QUERY_LENGTH:
            raise ValidationError(
                {
                    "q": (
                        f"Search query must contain at least "
                        f"{self.MIN_SEARCH_QUERY_LENGTH} characters."
                    )
                }
            )

        queryset = self.get_queryset().filter(
            username__icontains=query
        )

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)

class PublicUserDetailView(generics.GenericAPIView):
    """
    Return the public profile of a single user.

    Endpoint
    --------
    GET /api/v1/relationships/users/<uuid:id>/

    Purpose
    -------
    Provides a safe public representation of another user's profile.

    Phase 4 Rules
    -------------
    - Authentication required.
    - User must exist.
    - User must be active.
    - Blocked users cannot view each other's profiles.
    - Only public information is returned.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PublicUserSerializer
    lookup_field = "id"

    def get_queryset(self):
        """
        Base queryset used for profile discovery.

        Only active users are considered discoverable.
        Profile is loaded in the same query to avoid N+1 lookups
        when PublicUserSerializer accesses profile.bio.
        """

        return (
            User.objects.filter(is_active=True)
            .select_related("profile")
        )

    def get(self, request, *args, **kwargs):
        """
        Retrieve a single public profile.

        Security
        --------
        A blocked relationship (in either direction) makes the
        requested profile inaccessible.

        A 404 response is returned when the profile is not
        accessible, avoiding disclosure of whether the user
        exists but is hidden by relationship policy.
        """

        target_user = get_object_or_404(
            self.get_queryset(),
            id=kwargs[self.lookup_field],
        )

        if not can_view_profile(request.user, target_user):
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(
            target_user,
            context=self.get_serializer_context(),
        )

        return Response(serializer.data)        