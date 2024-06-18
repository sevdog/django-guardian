from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import Q
from guardian.core import ObjectPermissionChecker
from guardian.ctypes import get_content_type
from guardian.exceptions import ObjectNotPersisted
from guardian.shortcuts import _handle_pk_field
from django.contrib.auth.models import Permission

import warnings


def _ensure_permission(perm, ctype):
    if not isinstance(perm, Permission):
        perm = Permission.objects.get(content_type=ctype, codename=perm)

    return perm


def _get_perm_filter(perm, model):
    if isinstance(perm, Permission):
        return Q(permission=perm)
    return Q(
        permission__codename=perm, permission__content_type=get_content_type(model)
    )


class BaseObjectPermissionManager(models.Manager):

    @property
    def user_or_group_field(self):
        try:
            self.model._meta.get_field("user")
            return "user"
        except FieldDoesNotExist:
            return "group"

    def is_generic(self):
        try:
            self.model._meta.get_field("object_pk")
            return True
        except FieldDoesNotExist:
            return False

    def assign_perm(self, perm, user_or_group, obj):
        """
        Assigns permission with given ``perm`` for an instance ``obj`` and
        ``user``.
        """
        if getattr(obj, "pk", None) is None:
            raise ObjectNotPersisted("Object %s needs to be persisted first" % obj)
        ctype = get_content_type(obj)
        kwargs = {
            "permission": _ensure_permission(perm, ctype),
            self.user_or_group_field: user_or_group,
        }
        if self.is_generic():
            kwargs["content_type"] = ctype
            kwargs["object_pk"] = obj.pk
        else:
            kwargs["content_object"] = obj
        obj_perm, _ = self.get_or_create(**kwargs)
        return obj_perm

    def bulk_assign_perm(self, perm, user_or_group, queryset):
        """
        Bulk assigns permissions with given ``perm`` for an objects in ``queryset`` and
        ``user_or_group``.
        """
        if isinstance(queryset, list):
            ctype = get_content_type(queryset[0])
        else:
            ctype = get_content_type(queryset.model)

        permission = _ensure_permission(perm, ctype)
        checker = ObjectPermissionChecker(user_or_group)
        checker.prefetch_perms(queryset)

        def _instance_builder(instance):
            kwargs = {
                "permission": permission,
                self.user_or_group_field: user_or_group,
            }
            if self.is_generic():
                kwargs["content_type"] = ctype
                kwargs["object_pk"] = instance.pk
            else:
                kwargs["content_object"] = instance
            return self.model(**kwargs)

        return self.model.objects.bulk_create(
            (
                _instance_builder(instance)
                for instance in queryset
                if not checker.has_perm(permission.codename, instance)
            ),
            ignore_conflicts=True,
        )

    def assign_perm_to_many(self, perm, users_or_groups, obj):
        """
        Bulk assigns given ``perm`` for the object ``obj`` to a set of users or a set of groups.
        """
        ctype = get_content_type(obj)
        kwargs = {"permission": _ensure_permission(perm, ctype)}
        if self.is_generic():
            kwargs["content_type"] = ctype
            kwargs["object_pk"] = obj.pk
        else:
            kwargs["content_object"] = obj

        field = self.user_or_group_field
        return self.model.objects.bulk_create(
            (self.model(**kwargs, **{field: user}) for user in users_or_groups),
            ignore_conflicts=True,
        )

    def assign(self, perm, user_or_group, obj):
        """Depreciated function name left in for compatibility"""
        warnings.warn(
            "UserObjectPermissionManager method 'assign' is being renamed to 'assign_perm'. Update your code accordingly as old name will be depreciated in 2.0 version.",
            DeprecationWarning,
        )
        return self.assign_perm(perm, user_or_group, obj)

    def remove_perm(self, perm, user_or_group, obj):
        """
        Removes permission ``perm`` for an instance ``obj`` and given ``user_or_group``.

        Please note that we do NOT fetch object permission from database - we
        use ``Queryset.delete`` method for removing it. Main implication of this
        is that ``post_delete`` signals would NOT be fired.
        """
        if getattr(obj, "pk", None) is None:
            raise ObjectNotPersisted(f"Object {obj} needs to be persisted first")

        filters = Q(**{self.user_or_group_field: user_or_group}) & _get_perm_filter(
            perm, obj
        )
        if self.is_generic():
            filters &= Q(object_pk=obj.pk)
        else:
            filters &= Q(content_object__pk=obj.pk)
        return self.filter(filters).delete()

    def bulk_remove_perm(self, perm, user_or_group, queryset):
        """
        Removes permission ``perm`` for a ``queryset`` and given ``user_or_group``.

        Please note that we do NOT fetch object permission from database - we
        use ``Queryset.delete`` method for removing it. Main implication of this
        is that ``post_delete`` signals would NOT be fired.
        """
        filters = Q(**{self.user_or_group_field: user_or_group}) & _get_perm_filter(
            perm, queryset.model
        )
        if self.is_generic():
            filters &= Q(object_pk__in=queryset.values(_handle_pk_field(queryset, 'pk')))
        else:
            filters &= Q(content_object__in=queryset)

        return self.filter(filters).delete()


class UserObjectPermissionManager(BaseObjectPermissionManager):
    pass


class GroupObjectPermissionManager(BaseObjectPermissionManager):
    pass
