from django.forms import ModelForm
from django import forms

base_class = 'min-w-full '

def get_field_classes(widget:forms.Widget,extra=''):
    
    class_name  = widget.__class__.__name__
    
    if isinstance(widget,(forms.TextInput,forms.NumberInput)):
        return 'input ' + extra
    elif isinstance(widget,(forms.SelectMultiple,forms.Select,)):
        
        if isinstance(widget,(forms.SelectMultiple,)):
            return 'input min-h-48 ' + extra
        
        return  'select ' + extra

    elif isinstance(widget,(forms.Textarea,)):
        return 'textarea ' + extra
    
    elif isinstance(widget,(forms.FileInput,)):
        return 'file-input '+ extra
    
    elif isinstance(widget,(forms.CheckboxInput,)):
        return 'checkbox ' + extra.replace("min-w-full"," ").replace("w-full"," ")

    return ' ' + extra

class DynamicModelForm(ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            # Base Tailwind classes for inputs
            base_class = ' min-w-full bg-base-200 '
            classes = get_field_classes(field.widget,base_class)
            

            # Merge with existing classes if any
            if field.widget.attrs.get("class"):
                field.widget.attrs["class"] += " " + classes
            else:
                field.widget.attrs["class"] = classes

    @classmethod
    def form_factory(cls,model,fields):
        
        meta_class = type("Meta",(),{
            'model':model,
            'fields':fields
        })
        
        form = type("DynamicForm",(DynamicModelForm,),{'Meta':meta_class})
        
        return form


class DynamicInlineFormsetModelForm(ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            # Base Tailwind classes for inputs
            classes = get_field_classes(field.widget)
            # Add dark mode
            classes += " min-w-[100px]"
            # Merge with existing classes if any
            if field.widget.attrs.get("class"):
                field.widget.attrs["class"] += " " + classes
            else:
                field.widget.attrs["class"] = classes
