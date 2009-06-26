# django imports
from django import template
from django.contrib.contenttypes.models import ContentType

# portlets imports
import portlets.utils
from portlets.models import PortletBlocking
from portlets.models import Slot

register = template.Library()

# TODO: Make a better reuse of django-portlets portlet slot
@register.inclusion_tag('portlets/portlet_slot.html', takes_context=True)
def lfs_portlet_slot(context, slot_name):
    """Returns the portlets for given slot and instance. If the instance
    implements the ``get_parent_for_portlets`` method the portlets of the
    parent of the instance are also added.
    """
    instance = context.get("category") or context.get("product")

    if instance is None:
        return { "portlets" : [] }

    try:
        slot = Slot.objects.get(name=slot_name)
    except Slot.DoesNotExist:
        return { "portlets" : [] }

    # Get portlets for given instance
    temp = portlets.utils.get_portlets(slot, instance)

    # Get inherited portlets
    try:
        instance.get_parent_for_portlets()
    except AttributeError:
        instance = None

    while instance:
        # If the portlets are blocked no portlets should be added
        if portlets.utils.is_blocked(instance, slot):
            break

        # If the instance has no get_parent_for_portlets, there are no portlets
        try:
            instance = instance.get_parent_for_portlets()
        except AttributeError:
            break

        # If there is no parent for portlets, there are no portlets to add
        if instance is None:
            break

        parent_portlets = portlets.utils.get_portlets(slot, instance)
        parent_portlets.reverse()
        for p in parent_portlets:
            if p not in temp:
                temp.insert(0, p)

    rendered_portlets = []
    for portlet in temp:
        rendered_portlets.append(portlet.render(context))

    return { "portlets" : rendered_portlets }