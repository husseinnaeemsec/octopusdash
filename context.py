from .admin.registry import admin

def octopusdash_context(request):
    
    prefrence= None
    

    return {
        'registry':admin.get_registry(),
        'plugins':admin.get_plugins(),
        'prefrence':prefrence
        
    }


