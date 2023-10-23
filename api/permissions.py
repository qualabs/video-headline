from rest_framework import permissions


class OnlySuperusersPermission(permissions.BasePermission):
    message = 'Only Superusers are allowed to access.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser
