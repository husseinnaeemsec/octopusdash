from .base import BaseWidget
from django import forms


class DragDropFileInput(BaseWidget,forms.FileInput):
    
    template_name = 'od/widgets/custom/dragdropfileinput.html'
    name = 'Drag Drop File Input Widget'
    
    
    class Media:
        js = ['od/js/drag_drop_file_input.js']