from rest_framework import permissions

AUTHOR_ONLY_METHOD = ('DELETE', 'PATCH')


class IsAuthenticatedAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or (
            request.method in AUTHOR_ONLY_METHOD and obj.author == request.user
        )
