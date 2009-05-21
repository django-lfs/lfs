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
def portlets_inline(request, object, template_name="manage/portlets/portlets_inline.html"):
    """Displays the assigned portlets for given object.
    """
    portlet_types = get_registered_portlets()
    ct = ContentType.objects.get_for_model(object)

    slots = []
    for slot in Slot.objects.all():

        temp = []
        for pa in PortletAssignment.objects.filter(
            slot=slot, content_id=object.id, content_type=ct.id):
            temp.append({
                "pa_id" : pa.id,
                "title" : pa.portlet.title,
                "type" : portlet_types.get(pa.portlet.__class__.__name__, ""),
            })

        slots.append({
            "id"   : slot.id,
            "name" : slot.name,
            "portlets" : temp,
        })

    return render_to_string(template_name, RequestContext(request, {
        "slots" : slots,
        "portlet_types" : PortletRegistration.objects.all(),
        "object" : object,
        "object_type_id" : ct.id,
    }))


@login_required
def add_portlet(request, object_type_id, object_id, template_name="manage/portlets/portlet_add.html"):
    """Form and logic to add a new portlet to the object with given type and id.
    """    
    # Get content type to which the portlet should be added
    object_ct = ContentType.objects.get(pk=object_type_id)
    object = object_ct.get_object_for_this_type(pk=object_id)
    
    # Get the portlet type
    portlet_type = request.REQUEST.get("portlet_type", "")

    if request.method == "GET":

        try:
            portlet_ct = ContentType.objects.get(model=portlet_type.lower())
            mc = portlet_ct.model_class()
            form = mc().form(prefix="portlet")
            return render_to_response(template_name, RequestContext(request, {
                "form" : form,
                "object_id" : object_id,
                "object_type_id" : object_ct.id,
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
                slot_id=slot_id, content=object, portlet=portlet, position=position)

            html = portlets_inline(request, object)

            result = simplejson.dumps({
                "html" : html,
                "message" : _(u"Portlet has been added.")},
                cls = LazyEncoder
            )
            return HttpResponse(result)

        except ContentType.DoesNotExist:
            pass

@login_required
def delete_portlet(request, portletassignment_id):
    """Deletes a portlet for given portlet assignment.
    """
    try:
        pa = PortletAssignment.objects.get(pk=portletassignment_id)
    except PortletAssignment.DoesNotExist:
        pass
    else:
        pa.delete()
        return lfs.core.utils.set_message_cookie(
            reverse("lfs_manage_product", kwargs={"product_id" : pa.content_id}),
            msg = _(u"Portlet has been deleted."))

@login_required
def edit_portlet(request, portletassignment_id, template_name="manage/portlets/portlet_edit.html"):
    """Form and logic to edit the portlet of the given portlet assignment.
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

        html = portlets_inline(request, pa.content)

        result = simplejson.dumps({
            "html" : html,
            "message" : _(u"Portlet has been saved.")},
            cls = LazyEncoder
        )
        return HttpResponse(result)