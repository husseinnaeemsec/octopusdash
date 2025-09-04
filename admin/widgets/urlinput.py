from .base import BaseWidget,DaisyInput
from django import forms
from django.utils.safestring import mark_safe


class URLInput(DaisyInput,forms.URLInput):
    
    template_name = 'od/widgets/inputs/urlinput.html'
    name = 'Daisy URL input.'
    
    def __init__(self, validate=True,hint=None,title=None,pattern=None, attrs=None, icon=None):

        attrs = attrs or {}
        
        if title:
            attrs['title'] = title
        
        if  hint:
            attrs['hint'] = hint
            
        
        super().__init__(validate, pattern, attrs, icon)    

    def default_icon(self):
        return """
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5 opacity-50">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 0 1 1.242 7.244l-4.5 4.5a4.5 4.5 0 0 1-6.364-6.364l1.757-1.757m13.35-.622 1.757-1.757a4.5 4.5 0 0 0-6.364-6.364l-4.5 4.5a4.5 4.5 0 0 0 1.242 7.244" />
        </svg>

        """