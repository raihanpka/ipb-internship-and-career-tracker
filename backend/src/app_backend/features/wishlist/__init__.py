"""
Wishlist Feature Package – Command Handlers untuk student wishlist.
"""

from app_backend.features.wishlist.add_wishlist import (
    AddWishlistCommand,
    AddWishlistResult,
    add_wishlist_command_handler,
)
from app_backend.features.wishlist.delete_wishlist import (
    DeleteWishlistCommand,
    DeleteWishlistResult,
    delete_wishlist_command_handler,
)
from app_backend.features.wishlist.get_wishlist import (
    GetWishlistCommand,
    GetWishlistResult,
    get_wishlist_command_handler,
)
from app_backend.features.wishlist.list_wishlist import (
    ListWishlistCommand,
    ListWishlistResult,
    list_wishlist_command_handler,
)
from app_backend.features.wishlist.update_wishlist import (
    UpdateWishlistCommand,
    UpdateWishlistResult,
    update_wishlist_command_handler,
)

__all__ = [
    # Commands
    "AddWishlistCommand",
    "UpdateWishlistCommand",
    "DeleteWishlistCommand",
    "GetWishlistCommand",
    "ListWishlistCommand",
    # Results
    "AddWishlistResult",
    "UpdateWishlistResult",
    "DeleteWishlistResult",
    "GetWishlistResult",
    "ListWishlistResult",
    # Handlers
    "add_wishlist_command_handler",
    "update_wishlist_command_handler",
    "delete_wishlist_command_handler",
    "get_wishlist_command_handler",
    "list_wishlist_command_handler",
]
