# python imports
import urllib

# django imports
from django.contrib.auth.decorators import permission_required
from django.db import IntegrityError
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
from lfs.catalog.models import GroupsPropertiesRelation
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyGroup
from lfs.core.utils import LazyEncoder

class PropertyGroupForm(ModelForm):
    """
    """
    class Meta:
        model = PropertyGroup
        fields = ["name"]

@permission_required("manage_shop", login_url="/login/")
def manage_property_groups(request):
    """The main view to manage properties.
    """    
    try:
        property = PropertyGroup.objects.all()[0]
        url = reverse("lfs_manage_property_group", kwargs={"id": property.id})
    except IndexError:
        url = reverse("lfs_add_property_group")
    
    return HttpResponseRedirect(url)

@permission_required("manage_shop", login_url="/login/")
def manage_property_group(request, id, template_name="manage/properties/property_group.html"):
    """Edits property group with given id.
    """
    property_group = get_object_or_404(PropertyGroup, pk=id)
    if request.method == "POST":
        form = PropertyGroupForm(instance=property_group, data=request.POST)
        if form.is_valid():
            new_property_group = form.save()
            msg = urllib.quote(_(u"Property group has been saved."))
            url = reverse("lfs_manage_property_group", kwargs={"id" : property_group.id})
            response = HttpResponseRedirect(url)
            response.set_cookie("message", msg)
            
            return response
    else:
        form = PropertyGroupForm(instance=property_group)
    
    return render_to_response(template_name, RequestContext(request, {
        "property_group" : property_group,
        "property_groups" : PropertyGroup.objects.all(),
        "properties" : properties_inline(request, id),
        "form" : form,
        "current_id" : int(id),
    }))

@permission_required("manage_shop", login_url="/login/")
def properties_inline(request, id, template_name="manage/properties/properties_inline.html"):
    """
    """
    property_group = get_object_or_404(PropertyGroup, pk=id)
    
    gps = GroupsPropertiesRelation.objects.filter(group=id)
    
    # Calculate assignable properties
    assigned_property_ids = [p.property.id for p in gps]
    assignable_properties = Property.objects.exclude(
        pk__in=assigned_property_ids).exclude(local=True)

    return render_to_string(template_name, RequestContext(request, {
        "property_group" : property_group,
        "properties" : assignable_properties,
        "gps" : gps,
    }))

@permission_required("manage_shop", login_url="/login/")    
def add_property_group(request, template_name="manage/properties/add_property_group.html"):
    """Adds a new property group
    """
    if request.method == "POST":
        form = PropertyGroupForm(data=request.POST)
        if form.is_valid():
            property_group = form.save()

            msg = urllib.quote(_(u"Property group has been added."))
            url = reverse("lfs_manage_property_group", kwargs={"id" : property_group.id})
            response = HttpResponseRedirect(url)
            response.set_cookie("message", msg)

            return response
    else:
        form = PropertyGroupForm()

    return render_to_response(template_name, RequestContext(request, {
        "form" : form,
        "property_groups" : PropertyGroup.objects.all(),        
    }))

@permission_required("manage_shop", login_url="/login/")    
def delete_property_group(request, id):
    """Deletes the property group with passed id.
    """
    property_group = get_object_or_404(PropertyGroup, pk=id)    
    property_group.delete()

    msg = urllib.quote(_(u"Property group has been deleted."))
    response = HttpResponseRedirect(reverse("lfs_manage_property_groups"))
    response.set_cookie("message", msg)

    return response

@permission_required("manage_shop", login_url="/login/")
def assign_properties(request, group_id):
    """Assignes given properties (via request body) to passed group id.
    """
    for property_id in request.POST.getlist("property-id"):
        try:
            GroupsPropertiesRelation.objects.create(group_id=group_id, property_id=property_id)
        except IntegrityError:
            pass 
    
    _udpate_positions(group_id)
    result = simplejson.dumps({
        "html" : properties_inline(request, group_id),
        "message" : _(u"Properties have been assigned.")
    }, cls=LazyEncoder);
        
    return HttpResponse(result)

@permission_required("manage_shop", login_url="/login/")    
def update_properties(request, group_id):
    """Update or Removes given properties (via request body) from passed group id.
    """
    if request.POST.get("action") == "remove":
        for property_id in request.POST.getlist("property-id"):
            try:
                gp = GroupsPropertiesRelation.objects.get(group=group_id, property=property_id)
            except GroupsPropertiesRelation.DoesNotExist:
                pass
            else:
                gp.delete()
        
        message = _(u"Properties have been removed.")
                
    else:
        for gp in GroupsPropertiesRelation.objects.filter(group=group_id):
            position = request.POST.get("position-%s" % gp.property.id, 999)
            gp.position = int(position)
            gp.save()
            message = _(u"Properties have been updated.")

    _udpate_positions(group_id)
    result = simplejson.dumps({
        "html" : properties_inline(request, group_id),
        "message" : message
    }, cls=LazyEncoder);
        
    return HttpResponse(result)

def _udpate_positions(group_id):
    """
    """
    for i, gp in enumerate(GroupsPropertiesRelation.objects.filter(group=group_id)):
        gp.position = i+1
        gp.save()    