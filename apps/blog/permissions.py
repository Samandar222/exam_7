from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    - Anonymous: GET only (read).
    - Authenticated: GET + POST (create).
    - Owner: full CRUD.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if hasattr(obj, 'author'):
            return obj.author == request.user

        if hasattr(obj, 'user'):
            return obj.user == request.user

        return False
