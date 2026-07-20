from django.db import models

# Create your models here.
import uuid

from django.conf import settings
from django.db import models


class Block(models.Model):
    """
    Represents a relationship where one user blocks another.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    blocker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blocks_initiated",
    )

    blocked = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blocks_received",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("blocker", "blocked"),
                name="unique_block_relationship",
            ),
            models.CheckConstraint(
                condition=~models.Q(blocker=models.F("blocked")),
                name="prevent_self_block",
            ),
        ]

        indexes = [
            models.Index(fields=("blocker",)),
            models.Index(fields=("blocked",)),
        ]

        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.blocker} blocked {self.blocked}"