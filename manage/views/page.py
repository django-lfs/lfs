# python imports
import urllib

# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.core.widgets.file import LFSFileInput
from lfs.page.models import Page

class PageForm(ModelForm):
    """Form to edit a page.
    """
    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.fields["file"].widget = LFSFileInput()
    
    class Meta:
        model = Page

class PageAddForm(PageForm):
    """Form to add a page
    """
    class Meta:
        model = Page
        exclude = ("position",)

@permission_required("manage_shop", login_url="/login/")
def manage_pages(request):
    """Dispatches to the first page or to the form to add a page (if there is no 
    page yet).
    """
    try:
        page = Page.objects.all()[0]
        url = reverse("lfs_manage_page", kwargs={"id": page.id})
    except IndexError:
        url = reverse("lfs_add_page")
    
    return HttpResponseRedirect(url)

@permission_required("manage_shop", login_url="/login/")
def manage_page(request, id, template_name="manage/page/page.html"):
    """Provides a form to edit the page with the passed id.
    """
    page = get_object_or_404(Page, pk=id)
    if request.method == "POST":
        form = PageForm(instance=page, data=request.POST, files=request.FILES)
        if form.is_valid():
            new_page = form.save()
            _update_positions()

            msg = urllib.quote(_(u"Page has been saved."))
            url = reverse("lfs_manage_page", kwargs={"id" : page.id})
            response = HttpResponseRedirect(url)
            response.set_cookie("message", msg)
            
            return response
    else:
        form = PageForm(instance=page)
    
    return render_to_response(template_name, RequestContext(request, {
        "page" : page,
        "pages" : Page.objects.all(),
        "form" : form,
        "current_id" : int(id),
    }))

@permission_required("manage_shop", login_url="/login/")    
def add_page(request, template_name="manage/page/add_page.html"):
    """Provides a form to add a new page.
    """
    if request.method == "POST":
        form = PageAddForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            page = form.save()
            _update_positions()

            msg = urllib.quote(_(u"Page has been added."))
            url = reverse("lfs_manage_page", kwargs={"id" : page.id})
            response = HttpResponseRedirect(url)
            response.set_cookie("message", msg)

            return response
    else:
        form = PageAddForm()

    return render_to_response(template_name, RequestContext(request, {
        "form" : form,
        "pages" : Page.objects.all(),        
    }))

@permission_required("manage_shop", login_url="/login/")
def delete_page(request, id):
    """Deletes the page with passed id.
    """
    page = get_object_or_404(Page, pk=id)    
    page.delete()

    msg = urllib.quote(_(u"Page has been deleted."))
    response = HttpResponseRedirect(reverse("lfs_manage_pages"))
    response.set_cookie("message", msg)

    return response

def _update_positions():
    """Updates the positions of all pages.
    """
    for i, page in enumerate(Page.objects.all()):
        page.position = (i+1)*10
        page.save()