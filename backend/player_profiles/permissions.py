from rest_framework.permissions import IsAuthenticated

class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return bool(super().has_permission(request, view) and request.user.role.name == 'Admin')
