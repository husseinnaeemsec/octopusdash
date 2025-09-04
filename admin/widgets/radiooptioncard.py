from .base import WidgetWithOptionAttrs
from django import forms

class RadioOptionCard(WidgetWithOptionAttrs,forms.RadioSelect):
    template_name = 'od/widgets/custom/radiooptioncard.html'
    

