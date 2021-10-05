from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    message = "Для внесения изменений необходимы админские права"

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == request.user.is_superuser