from django.dispatch import Signal
from .admin.plugins.registry import plugins_registry
from .admin.utils import load_plugins
from django.dispatch import receiver


delete_plugin_signal = Signal()
refresh_plugins_registry_signal = Signal()


@receiver(delete_plugin_signal)
def handle_remove_plugin(sender, plugin_name, **kwargs):
    """
    When a plugin is removed, update the registry.
    """
    if plugin_name in plugins_registry.get_registry().keys():
        plugins_registry.delete(plugin_name)
        print(f"Plugin '{plugin_name}' removed from registry.")
    else:
        print(f"Plugin '{plugin_name}' was not in registry.")

@receiver(refresh_plugins_registry_signal)
def refresh_registry(sender,**kwagrs):
    plugins_registry.set(load_plugins())