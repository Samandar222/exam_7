from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Anonymous users can only read.
    Authenticated users can create/read.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
