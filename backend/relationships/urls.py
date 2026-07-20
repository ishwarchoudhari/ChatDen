# relationships/urls.py
from django.urls import path

from .views import (
    BlockDeleteView,
    BlockListCreateView,
    PublicUserDetailView,
    UserSearchView,
)

app_name = "relationships"

urlpatterns = [
    # ----------------------------
    # Blocking API
    # ----------------------------
    path("blocks/", BlockListCreateView.as_view(), name="block-list-create"),
    path("blocks/<uuid:id>/", BlockDeleteView.as_view(), name="block-delete"),
    # ----------------------------
    # User Discovery API
    # ----------------------------
    path("search/", UserSearchView.as_view(), name="user-search"),
    path("users/<uuid:id>/", PublicUserDetailView.as_view(), name="public-user-detail"),
]