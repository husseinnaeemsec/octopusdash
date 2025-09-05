import importlib.util
from pathlib import Path
from django.conf import settings
import sys
import shutil

import sys
import importlib.util
from pathlib import Path
from django.conf import settings

def load_plugins(base_dir=settings.BASE_DIR):
    plugins = {}
    plugins_path = Path(base_dir) / "plugins"

    if not plugins_path.exists() or not plugins_path.is_dir():
        print("No plugins folder found.")
        return plugins

    for path in plugins_path.iterdir():
        # Skip hidden files/folders
        if path.name.startswith("_"):
            continue

        # Single-file plugin
        if path.is_file() and path.suffix == ".py":
            module_name = path.stem
            spec = importlib.util.spec_from_file_location(module_name, path)

        # Package plugin
        elif path.is_dir() and (path / "__init__.py").exists():
            module_name = path.name
            spec = importlib.util.spec_from_file_location(module_name, path / "__init__.py")

            # Add assets folder to STATICFILES_DIRS
            assets_dir = path / "assets"
            if assets_dir.exists() and assets_dir.is_dir():
                if str(assets_dir) not in settings.STATICFILES_DIRS:
                    settings.STATICFILES_DIRS += (str(assets_dir),)
                    print(f"Added {module_name} assets to STATICFILES_DIRS")

        else:
            continue

        # Load module dynamically
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module  # ensures relative imports work
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"Error loading plugin {module_name}: {e}")
            continue

        # Extract plugin info
        plugin_info = getattr(module, "plugin", None)
        if plugin_info:
            plugins[module_name] = plugin_info
        else:
            print(f"No 'plugin' variable found in {module_name}")

    return plugins





def delete_plugin(base_dir: str, plugin_name: str):
    """
    Fully uninstall a plugin:
    - Runs its teardown() hook if available
    - Removes the module from sys.modules
    - Deletes plugin files/folder from disk
    """

    plugins_path = Path(base_dir) / "plugins"

    # 1. Try to load the plugin module to get teardown
    plugin_module_path = None
    if (plugins_path / f"{plugin_name}.py").exists():
        plugin_module_path = plugins_path / f"{plugin_name}.py"
    elif (plugins_path / plugin_name / "__init__.py").exists():
        plugin_module_path = plugins_path / plugin_name / "__init__.py"

    plugin_info = None
    if plugin_module_path:
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_module_path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            plugin_info = getattr(module, "plugin", None)
        except Exception as e:
            print(f"Warning: could not load plugin {plugin_name} for teardown: {e}")

    # 2. Run teardown if available
    if plugin_info:
        teardown = plugin_info.get("teardown") if isinstance(plugin_info, dict) else None
        if callable(teardown):
            try:
                teardown()
                print(f"Teardown executed for {plugin_name}.")
            except Exception as e:
                print(f"Error during teardown of {plugin_name}: {e}")

    # 3. Unload module from sys.modules
    if plugin_name in sys.modules:
        del sys.modules[plugin_name]
        print(f"Unloaded {plugin_name} from memory.")

    # 4. Remove plugin files/folder
    plugin_path_file = plugins_path / f"{plugin_name}.py"
    plugin_path_dir = plugins_path / plugin_name

    if plugin_path_file.exists():
        plugin_path_file.unlink()
        print(f"Deleted file plugin {plugin_name}.py")
        return True
    elif plugin_path_dir.exists():
        shutil.rmtree(plugin_path_dir)
        print(f"Deleted plugin folder {plugin_name}/")
        return True
    else:
        print(f"No plugin files found for {plugin_name}.")
        return False