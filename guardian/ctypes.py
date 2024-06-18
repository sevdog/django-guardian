from functools import lru_cache

from django.contrib.contenttypes.models import ContentType
from django.utils.module_loading import import_string

from guardian.conf import settings as guardian_settings


def get_content_type(obj):
    get_content_type_function = import_string(
        guardian_settings.GET_CONTENT_TYPE)
    return get_content_type_function(obj)


def get_default_content_type(obj):
    return ContentType.objects.get_for_model(obj)


@lru_cache(None)
def _get_ct_cached(app_label, codename):
    """
    Caches ``ContentType`` instances like its ``QuerySet`` does.
    """
    return ContentType.objects.get(
        app_label=app_label,
        permission__codename=codename,
    )
