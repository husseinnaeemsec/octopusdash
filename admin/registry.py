from ._exceptions import *
from django.db import models
from .base import ModelAdmin


class Admin:
    
    _registry = {}
    _plugins = set()
    
    def register_plugin(self,plugin):
        self._plugins.add(plugin)
    
    def register(self,model:models.Model,admin=None):
        opts = model._meta
        read_only_field = []
        
        for field in opts.fields:
            if not field.editable:
                read_only_field.append(field.name)
        
        if self._registry.get(opts.app_label):
            self._registry[opts.app_label]['models'][opts.model_name] = {
                'model':model,
                'admin':admin(model) if admin else ModelAdmin(model)
            }
        else:
            self._registry[opts.app_label] = {
                'config':opts.app_config,
                'models':{ opts.model_name:{ 'model':model , 'admin':admin(model) if admin else ModelAdmin(model) } }
            }
    def get_registry(self):
        return self._registry

    def get_plugins(self):
        return self._plugins

    def get_app(self,app_label):
        
        return self._registry.get(app_label,None)

    def get_model(self,app_label,model_name):
        app = self.get_app(app_label)
        if app is None:
            return None
        return app.get("models").get(model_name,None)

    def get_urls(self):
        
        urls = []
        
        for app_label,app_data in self._registry.items():
            
            for model_name,model_data in app_data.get("models").items():
                urls.extend(model_data['admin'].urls)
        
        return urls

    @property
    def urls(self):
        
        return self.get_urls()

admin = Admin()