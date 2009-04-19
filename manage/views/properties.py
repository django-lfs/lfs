# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.core.utils
from lfs.core.utils import LazyEncoder
from lfs.core.signals import property_type_changed
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyOption

class PropertyDataForm(ModelForm):
    """
    """
    class Meta:
        model = Property
        fields = ["name", "filterable", "unit"]

class PropertyTypeForm(ModelForm):
    """
    """
    class Meta:
        model = Property
        fields = ["type"]

class StepsForm(ModelForm):
    """
    """
    class Meta:
        model = Property
        fields = ["step"]
    
@permission_required("manage_shop", login_url="/login/")    
def manage_properties(request):
    """The main view to manage properties.
    """
    try:
        property = Property.objects.filter(local=False)[0]
        url = reverse("lfs_manage_shop_property", kwargs={"id": property.id})
    except IndexError:
        url = reverse("lfs_add_shop_property")
    
    return HttpResponseRedirect(url)

@permission_required("manage_shop", login_url="/login/")    
def manage_property(request, id, template_name="manage/properties/property.html"):
    """
    """    
    property = get_object_or_404(Property, pk=id)
    if request.method == "POST":
        form = PropertyDataForm(instance=property, data=request.POST)
        if form.is_valid():
            new_property = form.save()

            return lfs.core.utils.set_message_cookie(
                url = reverse("lfs_manage_shop_property", kwargs={"id" : property.id}),
                msg = _(u"Property type has been saved."),
            )        
            
    else:
        form = PropertyDataForm(instance=property)
    
    return render_to_response(template_name, RequestContext(request, {
        "property" : property,
        "properties" : Property.objects.filter(local=False),
        "form" : form,
        "type_form" : PropertyTypeForm(instance=property),
        "current_id" : int(id),
        "options" : options_inline(request, id),
        "steps" : steps_inline(request, id),
    }))

@permission_required("manage_shop", login_url="/login/")    
def update_property_type(request, id):
    """Updates the type of the property.
    
    This is separated from the data, because a change of type causes a deletion
    of product property values
    """
    property = get_object_or_404(Property, pk=id)
    old_type = property.type
    form = PropertyTypeForm(instance=property, data=request.POST)
    new_property = form.save()
        
    # Send signal only when the type changed as all values are deleted.
    if old_type != new_property.type:
        property_type_changed.send(property)

    return lfs.core.utils.set_message_cookie(
        url = reverse("lfs_manage_shop_property", kwargs={"id" : property.id}),
        msg = _(u"Property type has been changed."),
    )        

@permission_required("manage_shop", login_url="/login/")
def steps_inline(request, property_id, template_name="manage/properties/steps_inline.html"):
    """Display the steps of a propety. Factored out for Ajax requests.
    """
    property = get_object_or_404(Property, pk=property_id)

    form = StepsForm(instance=property)
    return render_to_string(template_name, RequestContext(request, {
        "property" : property,
        "form" : form,
    }))

def save_steps(request, property_id):
    """Save the steps of property with given id.
    """    
    property = get_object_or_404(Property, pk=property_id)
    
    form = StepsForm(instance=property, data=request.POST)    
    property = form.save()

    result = simplejson.dumps({
        "steps" : steps_inline(request, property_id),
        "message" : _(u"Steps have been saved."),
    }, cls = LazyEncoder)
    
    return HttpResponse(result)

@permission_required("manage_shop", login_url="/login/")
def options_inline(request, property_id, template_name="manage/properties/options_inline.html"):
    """Display the options of a propety. Factored out for Ajax requests.
    """
    property = get_object_or_404(Property, pk=property_id)
    return render_to_string(template_name, RequestContext(request, {
        "property" : property,
    }))
    
@permission_required("manage_shop", login_url="/login/")
def add_property(request, template_name="manage/properties/add_property.html"):
    """Adds a new property.
    """
    if request.method == "POST":
        form = PropertyDataForm(data=request.POST)
        if form.is_valid():
            property = form.save()

            return lfs.core.utils.set_message_cookie(
                url = reverse("lfs_manage_shop_property", kwargs={"id" : property.id}),
                msg = _(u"Property has been added."),
            )        
    else:
        form = PropertyDataForm()

    return render_to_response(template_name, RequestContext(request, {
        "form" : form,
        "properties" : Property.objects.filter(local=False),
    }))

@permission_required("manage_shop", login_url="/login/")
def delete_property(request, id):
    """Deletes the property with given id.
    """
    try:
        property = Property.objects.get(pk=id)
    except Property.DoesNotExist:
        url = request.META.get("HTTP_REFERER", reverse("lfs_manage_shop_property"))
    else:
        property.delete()        
        url = reverse("lfs_manage_shop_properties")
        
    return HttpResponseRedirect(url)

@permission_required("manage_shop", login_url="/login/")
def add_option(request, property_id):
    """Adds option to property with passed property id.
    """
    property = get_object_or_404(Property, pk=property_id)
    
    if request.POST.get("action") == "add":
        name = request.POST.get("name", "")
        if name != "":
            option = PropertyOption.objects.create(name=name, property_id=property_id)
        message = _(u"Option has been added.")
    else:
        
        for option_id in request.POST.getlist("option"):
            
            try:
                option = PropertyOption.objects.get(pk=option_id)
            except PropertyOption.DoesNotExist:
                pass
            else:
                option.position = request.POST.get("position-%s" % option_id, 99)
                option.name = request.POST.get("name-%s" % option_id, "") 
                option.save()
        message = _(u"Options have been update.")

    _update_positions(property)
    result = simplejson.dumps({
        "options" : options_inline(request, property_id),
        "message" : message
    }, cls = LazyEncoder)
    
    return HttpResponse(result)

@permission_required("manage_shop", login_url="/login/")    
def delete_option(request, id):
    """Deletes option with given id.
    """
    try:        
        option = PropertyOption.objects.get(pk=id)
    except option.DoesNotExist:
        url = request.META.get("HTTP_REFERER", reverse("lfs_manage_shop_property"))
    else:
        property = option.property
        url = reverse("lfs_manage_shop_property", kwargs={"id" : property.id})
        option.delete()        
        _update_positions(property)
    
    return HttpResponseRedirect(url)
    
def _update_positions(property):
    """Updates position of options of given property.
    """
    for i, option in enumerate(property.options.all()):
        option.position = i+1
        option.save()
