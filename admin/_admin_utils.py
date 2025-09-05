from django.core.exceptions import ImproperlyConfigured
from django.forms import modelformset_factory, BaseModelFormSet
from octopusdash.admin.forms import DynamicInlineFormsetModelForm,DynamicModelForm
from django.db import connection
from django.db import models
from django.db.models import Q, CharField, TextField
from django.db.models.fields.json import JSONField

# Only import Postgres features if available
try:
    from django.contrib.postgres.search import SearchVector
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False
 
 
from django.db import connection

class BaseModelAdmin:
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
    # Filters
    auto_load_filters = True
    filter_fileds = []
    
    # Quick actions
    enable_quick_actions = False
    quick_actions = []
    
    def __init__(self,model:models.Model):
        self.model = model
        self.opts = model._meta
        self.actions = {}
        self.search_fields = self.search_fields or []
        self.filter_fileds = self.filter_fileds or []
        self.list_display = self.list_display or []
        self.list_editable = self.list_editable or []
        self.form_fields = self.form_fields or []
        self.exclude = self.exclude or []
        self.ordering = self.ordering or  []
        self.quick_actions = self.quick_actions or []
        self.enable_quick_actions = self.enable_quick_actions if self.enable_quick_actions is not None else False
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
    

    def is_postgres(self):
        """Check if current DB is PostgreSQL."""
        return connection.vendor == "postgresql"


    def build_search_q(self, search_term):
        """
        Build an OR-based search filter (Q object) for allowed fields.
        Expects get_search_fields() to return a list of tuples: (field_name, field)
        Returns None if no valid search fields exist.
        """
        if not search_term:
            return None

        q_obj = Q()
        search_fields = self.get_search_fields()  # [(field_name, field), ...]

        for field_name, field in search_fields:
            # Only allow text-like fields
            if isinstance(field, (CharField, TextField, JSONField)):
                q_obj |= Q(**{f"{field_name}__icontains": search_term})

        # If no valid fields, return a Q that matches nothing
        if q_obj.children:
            return q_obj
        else:
            # Q(pk__in=[]) will return empty queryset
            return Q(pk__in=[])

class FieldFalidationAndSearchMixin:
    computed_fields = []
    # --- Check if the models uses postgres

    # --- Core helpers ---
    def _get_model_fields(self):
        """Return all valid field names for the model."""
        return {f.name for f in self.model._meta.get_fields()}

    def _filter_valid_fields(self, fields):
        """Return only valid fields for the model."""
        valid_fields = self._get_model_fields()
        return [f for f in fields if f in valid_fields]

    # --- Specific field group getters ---
    def get_search_fields(self):
        """Return only valid search fields."""
        
        search_fields = getattr(self,'search_fields',[])
        # A list of tuples (field_name,field)
        search_fields_pairs = []
        valid_search_fields = set(['CharField','SlugField','TextField','JSONField'])

        if len(search_fields) == 0:
            for field in self.opts.fields:
                class_name = field.__class__.__name__
                if class_name in valid_search_fields:
                    search_fields.append(field.name)
                    search_fields_pairs.append((field.name,field))

        self._filter_valid_fields(search_fields)
        return search_fields_pairs

    def get_readonly_fields(self):
        """Return only valid readonly fields."""
        return self._filter_valid_fields(getattr(self, "readonly_fields", []))

    def get_list_display(self):
        """
        Return list_display fields excluding:
          - readonly_fields
          - duplicates
        """
        raw = getattr(self, "list_display", [])
        readonly = set(self.get_readonly_fields())
        return [f for f in self._filter_valid_fields(raw) if f not in readonly] or ['__str__']

    def get_list_editable(self):
        """
        Return list_editable fields excluding:
          - readonly_fields
          - non-list_display fields
        """
        raw = getattr(self, "list_editable", [])
        readonly = set(self.get_readonly_fields())
        list_display = set(self.get_list_display())
        return [
            f for f in self._filter_valid_fields(raw)
            if f not in readonly and f in list_display
        ]

    def get_form_fields(self):
        """
        Return form_fields excluding readonly_fields.
        If no explicit form_fields are set, return all model fields except readonly_fields.
        """
        raw = getattr(self, "form_fields", None)
        readonly = set(self.get_readonly_fields())
        if raw is None:
            return [f for f in self._get_model_fields() if f not in readonly]
        return [f for f in self._filter_valid_fields(raw) if f not in readonly]

    def _validate_fields(self):
            """
            Validate that all fields in search_fields, list_display, list_editable,
            readonly_fields, and form_fields exist in the model.
            """
            # collect all lists (if missing, default to empty)
            field_groups = {
                "search_fields": getattr(self, "search_fields", []),
                "list_display": getattr(self, "list_display", []),
                "list_editable": getattr(self, "list_editable", []),
                "readonly_fields": getattr(self, "readonly_fields", []),
                "form_fields": getattr(self, "form_fields", []),
                "exclude":getattr(self,'exclude',[]),
            }

            # collect actual model fields (including related)
            valid_fields = {f.name for f in self.opts.get_fields()}

            errors = []

            for group_name, fields in field_groups.items():
                for field in fields:
                    if field not in valid_fields and group_name != 'list_display':
                        errors.append(f"'{field}' in {group_name} is not a valid field of {self.model.__name__}")
                    
                    elif field not in valid_fields and group_name == 'list_display':
                        self.computed_fields.append(field)

            if errors:
                raise ImproperlyConfigured(
                    f"Invalid field configuration for {self.model.__name__}:\n" +
                    "\n".join(errors)
                )



class FormsetMixin:
    extra = 0
    def get_form_class(self):
        """
        Build or return a model form class for this model.
        Respects form_fields, exclude, readonly_fields,
        and injects widgets from self.widgets if provided.
        """
        if self.form_class:
            return self.form_class

        effective_exclude = list(self.exclude) + list(self.readonly_fields)

        attrs = {
            "fields": self.form_fields or "__all__",
            "model": self.model,
            "exclude": effective_exclude or None,
        }

        # Dynamically add widgets if self.widgets is provided
        if hasattr(self, "widgets") and isinstance(self.widgets, dict):
            attrs["widgets"] = self.widgets

        meta_class = type("Meta", (), attrs)

        return type(
            f"{self.opts.model_name.capitalize()}DynamicFormClass",
            (DynamicModelForm,),
            {"Meta": meta_class},
        )

        
    def get_formset_form_class(self):
        effective_exclude = list(self.exclude) + list(self.readonly_fields)
        
        attrs = {
            'fields':self.form_fields or '__all__',
            'model':self.model,
            'exclude':effective_exclude or None
        }
        
        meta_class = type("Meta",(),attrs)
        
        return type(
            f"{self.opts.model_name.capitalize()}DynamicFormsetForm",
            (DynamicInlineFormsetModelForm,),
            {"Meta":meta_class}
        )

    def get_formset_class(self):
        """
        Return a formset class for the model.
        If `formset_class` is set, return it. Otherwise,
        generate one using `modelformset_factory`.
        """
        if self.formset_class:
            return self.formset_class

        formset_form_class = self.get_formset_form_class()

        return modelformset_factory(
            self.model,
            form=formset_form_class,
            formset=BaseModelFormSet,
            fields=self.form_fields or None,
            exclude=list(self.exclude) + list(self.readonly_fields),
            extra=self.extra,
        )


