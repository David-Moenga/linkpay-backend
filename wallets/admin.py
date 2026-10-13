from django.contrib import admin
from django.db import models as djmodels
from . import models as appmodels

for name in dir(appmodels):
    obj = getattr(appmodels, name)
    if isinstance(obj, type) and issubclass(obj, djmodels.Model) and obj is not djmodels.Model and not admin.site.is_registered(obj):
        try:
            admin.site.register(obj)
        except Exception:
            pass
