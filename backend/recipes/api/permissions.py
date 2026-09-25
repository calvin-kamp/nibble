from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """Anyone may read, only the owner may change or delete.

    Recipes without owner (seeded ones) are therefore read-only in the API.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.owner_id is not None and obj.owner_id == request.user.id
