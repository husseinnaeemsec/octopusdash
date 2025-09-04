from django.db import models
from django import forms
from . import views
from ._exceptions import *
from django.urls import path,reverse_lazy
from .forms import DynamicModelForm
from ._admin_utils import FieldFalidationMixin,FormsetMixin
from django.db.models import BooleanField,TimeField,DateField,DateTimeField,CharField,TextField
from functools import wraps

def action(short_description: str):
    """
    Decorator to mark a method as an admin action.
    Must be called on a ModelAdmin method.
    """
    if not short_description:
        raise ValueError("action decorator requires a short_description")

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        # Attach metadata
        wrapper.short_description = short_description
        wrapper.is_admin_action = True

        # Register the action on the instance when class is created
        if not hasattr(func, "_registered_actions"):
            func._registered_actions = []
        func._registered_actions.append(wrapper)

        return wrapper

    return decorator



class ModelAdmin(FieldFalidationMixin,FormsetMixin):
    # Widgt
    widgets = {}
    # Model
    model:models.Model|None = None 
    queryset = None
    # Fields
    search_fields:list = []
    readonly_fields:list = []
    list_display:list = []
    list_editable:list = []
    form_fields = []
    exclude = []
    ordering = ['id']
    # Forms
    form_class = None
    formset_class = None
    
    # Views
    list_view = None
    update_view = None
    delete_view = None
    create_view = None
    # Config
    icon:str|None = None
    # Actions
    actions = {}

    # Filters
    auto_load_filters = True
    filter_fileds = []

    
    def __init__(self,model:models.Model):
        self.model = model
        self.opts = model._meta
        self.actions = {}
        self.queryset = self.queryset or self.model.objects.all().order_by(*self.ordering)
        self._handle_custom_actions()
        self._validate_fields()

    def get_action(self,action):
        return self.actions.get(action,{}).get("action",None) 
    
    def each_context(self):
        
        return {
            'admin':self
        }

    def _handle_custom_actions(self):
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and getattr(attr, "is_admin_action", False):
                self.actions[attr_name] = {
                    'short_description':attr.short_description,
                    'action':attr
                }

    def get_actions(self):
        """Return the registered actions."""
        return self.actions
    
    def get_queryset(self):
        
        return 
    
    def get_list_view(self):
        annotations = {}
        context = self.each_context()

        for field in getattr(self, 'computed_fields', []):
            getter_name = f'get_{field}'
            if hasattr(self, getter_name) and callable(getattr(self, getter_name)):
                expr = getattr(self, getter_name)()
                if expr is None:
                    raise NotImplementedError(f"Computed field '{field}' must return a Django expression")
                annotations[field] = expr

        qs = self.queryset.annotate(**annotations)
        view = views.ModelListView.view_factory(self.model, context)
        view.admin = self
        view.queryset = qs
        view.object_list = qs
        
        return self.list_view or view

    
    def get_update_view(self):
        
        view = views.ModelUpdateView.view_factory(self.model,self.each_context())
        view.queryset = self.queryset
        view.form_class = self.get_form_class()
        view.success_url = self.list_url
        
        return self.update_view or view
    
    def get_delete_view(self):
        
        context = self.each_context()
        
        view = views.ModelDeleteView.view_factory(self.model,context)
        view.form_class = self.get_form_class()
        view.queryset = self.queryset
        view.success_url = self.list_url
        
        return self.delete_view or view
    
    def get_create_view(self):
        view = views.ModelCreateView.view_factory(self.model,self.each_context())
        view.form_class = self.get_form_class()
        view.queryset = self.queryset
        view.success_url = self.list_url
        
        return self.create_view or view
    
        
    
    def get_urls(self):
        
        return [
            path(f'{self.opts.app_label.lower()}/{self.opts.model_name.lower()}/',self.get_list_view().as_view(),name=f'{self.opts.model_name}-list-view'),
            path(f'{self.opts.app_label.lower()}/{self.opts.model_name.lower()}/update/<int:pk>/',self.get_update_view().as_view(),name=f'{self.opts.model_name}-update-view'),
            path(f'{self.opts.app_label.lower()}/{self.opts.model_name.lower()}/delete/<int:pk>/',self.get_delete_view().as_view(),name=f'{self.opts.model_name}-delete-view'),
            path(f'{self.opts.app_label.lower()}/{self.opts.model_name.lower()}/create/',self.get_create_view().as_view(),name=f'{self.opts.model_name}-create-view'),  
        ]
    

    @property
    def list_url(self):
        return reverse_lazy(f'{self.opts.model_name}-list-view')
    
    @property
    def create_url(self):
        
        return reverse_lazy(f'{self.opts.model_name}-create-view')

    
    def get_delete_url(self,pk:int,request):
        
        return reverse_lazy(f'{self.opts.model_name}-delete-view',kwargs={'pk':pk})

    def get_update_url(self,pk:int,request):
        
        return reverse_lazy(f"{self.opts.model_name}-update-view",kwargs={'pk':pk})

    @property
    def urls(self):
        return self.get_urls()
    


    def get_table_header(self) -> list[str]:
        """
        Return a list of field names for rendering table headers.
        Combines list_display and list_editable while preserving order
        and avoiding duplicates.
        """
        headers = []
        computed_fields = getattr(self,'computed_fields',[])
        # Start with list_display fields
        for field in self.get_list_display():
            headers.append(field)

        # Add list_editable fields that are not already included
        for field in self.get_list_editable():
            if field not in headers:
                headers.append(field)

        return headers + computed_fields

    def get_filter_fields(self):
        filter_fields_map = {}
        fields = self.filter_fileds or []
        
        allowed_types = (BooleanField, DateField, DateTimeField, TimeField, CharField, TextField)
        time_range_fields = (DateField, DateTimeField, TimeField)

        if  fields:
            for field in self.opts.get_fields():
                # Skip reverse relations & m2m auto-created fields
                if field.name in fields:
                    if not hasattr(field, "get_internal_type"):
                        continue

                    if isinstance(field, allowed_types):
                        field_type = field.get_internal_type()

                        # Input type mapping
                        input_type_map = {
                            "BooleanField": "radio",
                            "TimeField": "time",
                            "DateField": "date",
                            "DateTimeField": "datetime",
                        }
                        input_type = input_type_map.get(field_type, "text")

                        # Base field info
                        filter_fields_map[field.name] = {
                            "type": field_type,
                            "name": field.name,
                            "readable": field.name.replace("_", " ").capitalize(),
                            "input_type": input_type,
                            "lookup": []
                        }

                        # Lookup rules
                        if isinstance(field, time_range_fields):
                            filter_fields_map[field.name]["lookup"] = [
                                {"label": "From", "lookup_name": f"{field.name}__gte"},
                                {"label": "To", "lookup_name": f"{field.name}__lte"},
                            ]
                        elif isinstance(field, BooleanField):
                            filter_fields_map[field.name]["lookup"] = [
                                {"label": "Yes", "lookup_name": field.name, "value": True},
                                {"label": "No", "lookup_name": field.name, "value": False},
                                {"label": "All", "lookup_name": field.name, "value": None},

                            ]
                        elif isinstance(field, (CharField, TextField)):
                            filter_fields_map[field.name]["lookup"] = [
                                {"label": "Contains", "lookup_name": f"{field.name}__icontains"},
                                {"label": "Exact", "lookup_name": f"{field.name}__exact"},
                            ]

        return filter_fields_map