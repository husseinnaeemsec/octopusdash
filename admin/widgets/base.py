from django.forms import Widget
from django.utils.safestring import mark_safe
from octopusdash.admin.settings import settings

class BaseWidget(Widget):
    name = 'Base Widget.'
    description = 'this class is a base widget and can not be used.'.capitalize()
    version = '0.0.1'
    docs_url = 'https://github.com/husseinnaeemsec/octopusdash'
    category = 'base'
    author = 'Hussein Naeem'
    
    
    
    
    class Media:
        css = {}
        js = []

    def get_context(self, name, value, attrs):
        # Get Django’s default context
        context = super().get_context(name, value, attrs)

        # Add our custom metadata
        context["widget_info"] = {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "docs_url": self.docs_url,
            "author": self.author,
            "category": self.category,
        }
        return context

    def render(self, name, value, attrs=None, renderer=None):
        # Call Django’s default rendering
        html = super().render(name, value, attrs, renderer)

        # If docs are provided, append snippet
        if settings.get("SHOW_WIDGET_DOCS_LINK",False):
            if self.docs_url:
                docs_html = f"""
                <p class="my-2 text-xs">
                    For more information about this widget see 
                    <a class="underline text-primary" href="{self.docs_url}" target="_blank">
                        {self.name.title()} docs
                    </a>
                </p>
                """
                html += docs_html

        return mark_safe(html)


class WidgetWithOptionAttrs(BaseWidget):
    
    def __init__(self,option_attrs=None,attrs = None):
        
        attrs = attrs or {}
        self.option_attrs = option_attrs or {}
        super().__init__(attrs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        # Call the parent method to get the default option dict
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        
        option['option_attrs'] = self.option_attrs.get(value,{})
        
        return option

class DaisyInput(BaseWidget,Widget):
    
    def __init__(self,validate=False,pattern=None,attrs = None , icon = None ):
            attrs = attrs or {}
            attrs['icon'] = icon or self.default_icon()
            if pattern and validate:
                attrs['pattern'] = pattern
                attrs['validate'] = validate
            if 'required' not in attrs:
                attrs['required'] = True
            self.icon = icon or self.default_icon()
            super().__init__(attrs)
    
    def default_icon(self):
        return ''