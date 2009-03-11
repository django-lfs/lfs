from django import forms
from django.utils.safestring import mark_safe

class LFSImageInput(forms.FileInput):
    """A custom image widget which displays the current image.
    """
    def render(self, name, value, attrs=None):
        output = super(LFSImageInput, self).render(name, None, attrs=attrs)
        
        if value and hasattr(value, "url_60x60"):
            output += u"""<div><img src="%s" /></div>""" % value.url_60x60
        elif value and hasattr(value, "url"):
                output += u"""<div><img src="%s" /></div>""" % value.url
        return mark_safe(output)
