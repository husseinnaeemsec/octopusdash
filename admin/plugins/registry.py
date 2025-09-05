class PluginsRegistry():
    
    _registry = {}
    
    def set(self,plugins:dict):
        
        self._registry = plugins
    
    def get_registry(self):
        return self._registry

    def update(self,new):
        self._registry.update(new)


    def delete(self,plugin):
        
        if self._registry.get(plugin,None):
            del self._registry[plugin]

        return True

    def get(self,plugin):
        
        return self._registry.get(plugin,None)

plugins_registry = PluginsRegistry()
