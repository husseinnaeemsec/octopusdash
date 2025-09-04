from .admin.registry import admin
from .admin.settings import settings
from octopusdash.__info__ import __version__

def octopusdash_context(request):
    
    

    return {
        'registry':admin.get_registry(),
        'plugins':admin.get_plugins(),
        'settings':settings,
        'version':__version__
    }


