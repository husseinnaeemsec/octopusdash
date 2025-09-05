from django.apps import AppConfig


class OctopusdashConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'octopusdash'
    def ready(self):
        from . import signals
        from .admin.plugins.registry import plugins_registry
        from .admin.utils import load_plugins
        plugins_registry.set(load_plugins())
