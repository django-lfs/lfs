from django import forms
from django.utils.safestring import mark_safe

class LFSFileInput(forms.FileInput):
    """A custom file widget which displays the current file.
    """
    def render(self, name, value, attrs=None):
        output = super(LFSFileInput, self).render(name, None, attrs=attrs)
        if value and hasattr(value, "url"):
            output = u"""<div><a href="%s" />%s</a></div>""" % (value.url, value.name) + output
        return mark_safe(output)
