# lfs imports
from lfs.export.models import Script

def register(method, name):
    """Registers a new export logic.
    """
    try:
        Script.objects.get(
            module=method.__module__, method=method.__name__)
    except Script.DoesNotExist:
        try:
            Script.objects.create(
                module=method.__module__, method=method.__name__, name=name)
        except:
            # Fail silently
            pass