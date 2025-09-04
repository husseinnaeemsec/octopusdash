from .forms import DynamicModelForm
from django.forms import BaseModelFormSet


class InlineEditableFormSet(BaseModelFormSet):
    """
    Custom formset that tracks which fields are editable in list view.
    """
    editable_fields = []

    def __init__(self, *args, editable_fields=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.editable_fields = editable_fields or []
        # Mark fields as editable/non-editable on each form
        for form in self.forms:
            form._editable_fields = self.editable_fields

