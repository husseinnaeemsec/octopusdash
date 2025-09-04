from .admin.registry import admin
from .admin.settings import settings

def octopusdash_context(request):
    
    

    return {
        'registry':admin.get_registry(),
        'plugins':admin.get_plugins(),
        'settings':settings
    }


