# templatetags/custom_tags.py
from django import template
from octopusdash.admin import ModelAdmin

register = template.Library()

@register.filter
def getattr_field(obj, attr):
    return getattr(obj, attr, None)

@register.filter("callable")
def callable_(value):
    return callable(value)

@register.filter
def get_callable_name(value):
    
    return value.__name__

@register.filter
def split(value, separator=','):
    """Split a string by the given separator."""
    return value.split(separator)


@register.simple_tag
def admin_view_with_args(admin:ModelAdmin,view, pk, request):

    if view == 'delete':    
        return admin.get_delete_url(pk,request)
    
    return admin.get_update_url(pk,request)


@register.filter
def startswith(value:str,text:str):
    return value.startswith(text)



@register.filter
def is_active_route(path:str,other_path:str):
    
    if not other_path.startswith("/dashboard/"):
        
        if not other_path.endswith("/"):
            other_path = f"/dashboard/{other_path}/"         
        else:
            other_path = f"/dashboard/{other_path}"
    
    return path == other_path or path.startswith(other_path)

@register.filter('getattr')
def get_obj_attribute(obj,attribute):
    
    if attribute == '__str__':
        return str(obj)
    
    return getattr(obj,attribute,'')


@register.filter
def readable(value:str):
    
    return value.replace("_"," ").capitalize()


@register.filter
def get_field(form, field_name):
    """
    Return a form field bound widget by name.
    Usage: {{ form|get_field:"field_name" }}
    """
    try:
        return form[field_name]
    except KeyError:
        return ""

@register.filter
def get_formvalue(form, field_name):
    """
    Return a form field bound widget by name.
    Usage: {{ form|get_field:"field_name" }}
    """
    try:
        return form[field_name]
    except KeyError:
        return ""


@register.filter("dir")
def dir_obj(obj):
    
    return dir(obj)

