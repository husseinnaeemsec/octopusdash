# views.py
from django.shortcuts import render
from django.views.generic import TemplateView,ListView
from django import forms
from octopusdash.admin.widgets import URLInput
from octopusdash.admin.widgets.select import RadioOptionCard
from octopusdash.admin.widgets.file import DragDropFileInput
from octopusdash.models import AllFields

class AllFieldsForm(forms.ModelForm):
    
    class Meta:
        model = AllFields
        fields = '__all__'
        widgets = {
            'char_field':RadioOptionCard(),
            'file_field':DragDropFileInput()
            
        }


def index(request):


    return render(request, 'od/index.html', {'form': AllFieldsForm()})