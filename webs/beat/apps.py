"""Django Application configuration."""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

__all__ = ['BeatConfig']


class BeatConfig(AppConfig):
    """Default configuration for django_celery_beat app."""

    name = 'beat'
    # label = 'beat'
    verbose_name = _('任务管理')
