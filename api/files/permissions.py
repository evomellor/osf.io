from rest_framework import permissions

from api.base.utils import get_user_auth
from osf.models import FileNode

class CheckedOutOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, FileNode), 'obj must be a FileNode, got {}'.format(obj)

        if request.method in permissions.SAFE_METHODS:
            return True

        auth = get_user_auth(request)
        # Limited to osfstorage for the moment
        if obj.provider != 'osfstorage':
            return False
        return obj.checkout is None \
            or obj.checkout == auth.user \
            or obj.node.has_permission(auth.user, 'admin')


class IsPreprintFile(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, FileNode), 'obj must be a FileNode, got {}'.format(obj)

        if request.method == 'DELETE' and obj.node.preprint_file == obj and not obj.node._has_abandoned_preprint:
            return False

        return True
