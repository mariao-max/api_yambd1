from rest_framework.permissions import SAFE_METHODS, BasePermission


class UserIsModerator(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            return (
                request.user == obj.author
                or (request.user.is_authenticated
                    and request.user.is_moderator())
                or (request.user.is_authenticated
                    and request.user.is_admin())
            )


class UserIsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()


class UserIsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_staff
            or request.user.is_superuser
            or request.user.role == 'admin'
        )
