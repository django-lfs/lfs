# django imports
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# portlets imports
from portlets.utils import get_registered_portlets
from portlets.models import PortletAssignment
from portlets.models import PortletRegistration
from portlets.models import Slot

# lfs imports
import lfs.core.utils
from lfs.catalog.models import Product
from lfs.core.utils import LazyEncoder

@login_required
def portlets_inline(request, product, template_name="manage/product/portlets_inline.html"):
    """
    """
    portlet_types = get_registered_portlets()
    ct = ContentType.objects.get_for_model(product)

    slots = []
    for slot in Slot.objects.all():

        temp = []
        for assignment in PortletAssignment.objects.filter(
            slot=slot, content_id=product.id, content_type=ct.id):
            temp.append({
                "id" : assignment.id,
                "title" : assignment.portlet.title,
                "type" : portlet_types.get(assignment.portlet.__class__.__name__, ""),
            })

        slots.append({
            "id"   : slot.id,
            "name" : slot.name,
            "portlets" : temp,
        })

    return render_to_string(template_name, RequestContext(request, {
        "slots" : slots,
        "portlet_types" : PortletRegistration.objects.all(),
        "product" : product,
    }))


@login_required
def add_portlet(request, object_id, template_name="manage/product/portlet_add.html"):
    """
    """
    product = Product.objects.get(pk=object_id)
    portlet_type = request.REQUEST.get("portlet_type")
    
    if request.method == "GET":
        
        try:
            ct = ContentType.objects.get(model=portlet_type)
            mc = ct.model_class()
            form = mc().form(prefix="portlet")
            return render_to_response(template_name, RequestContext(request, {
                "form" : form,
                "page_id" : object_id,
                "portlet_type" : portlet_type,
                "slots" : Slot.objects.all(),
            }))
        except ContentType.DoesNotExist:
            pass    
    else:
        try:
            ct = ContentType.objects.get(model=portlet_type)
            mc = ct.model_class()   
            form = mc().form(prefix="portlet", data=request.POST)
            portlet = form.save()
            
            slot_id = request.POST.get("slot")
            position = request.POST.get("position")
            PortletAssignment.objects.create(
                slot_id=slot_id, content=product, portlet=portlet, position=position)
                
            html = portlets_inline(request, product)
        
            result = simplejson.dumps({
                "html" : html,
                "message" : _(u"Portlet has been added.")}, 
                cls = LazyEncoder
            )
            return HttpResponse(result)
                
        except ContentType.DoesNotExist:
            pass
    
    return HttpResponseRedirect(reverse("lfs_manage_product", kwargs={"product_id" : product.id}))

@login_required
def delete_portlet(request, slot_id, object_id, portlet_id):
    """
    """
    try:
        pa = PortletAssignment.objects.get(slot = slot_id, content_id = object_id, portlet_id = portlet_id)
    except PortletAssignment.DoesNotExist:
        pass
    else:
        pa.delete()

    page = Product.objects.get(pk=object_id)            
    return lfs.core.utils.set_message_cookie(
        reverse("lfs_manage_product", kwargs={"product_id" : object_id}), 
        msg = _(u"Portlet has been deleted."))

@login_required
def edit_portlet(request, portletassignment_id, template_name="manage/product/portlet_edit.html"):
    """
    """
    try:
        pa = PortletAssignment.objects.get(pk=portletassignment_id)
    except PortletAssignment.DoesNotExist:
        return ""

    product = Product.objects.get(pk=pa.content_id)

    if request.method == "GET":
        slots = []
        for slot in Slot.objects.all():
            slots.append({
                "id" : slot.id,
                "name" : slot.name,
                "selected" : slot.id == pa.slot.id,
            })

        form = pa.portlet.form(prefix="portlet")
        return render_to_response(template_name, RequestContext(request, {
            "form" : form,
            "portletassigment_id" : pa.id,
            "slots" : slots,
            "position" : pa.position,
        }))
    else:
        form = pa.portlet.form(prefix="portlet", data=request.POST)
        portlet = form.save()
        
        # Save the rest
        pa.slot_id = request.POST.get("slot")
        pa.position = request.POST.get("position")
        pa.save()
        
        page = Product.objects.get(pk=pa.content_id)
        html = portlets_inline(request, product)
        
        result = simplejson.dumps({
            "html" : html,
            "message" : _(u"Portlet has been saved.")}, 
            cls = LazyEncoder
        )
        return HttpResponse(result)
