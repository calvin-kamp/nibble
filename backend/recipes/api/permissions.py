from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """Anyone who may see a recipe may read it, only the author may change it.

    Recipes whose author deleted the account are read-only for good.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.author_id is not None and obj.author_id == request.user.profile.pk
