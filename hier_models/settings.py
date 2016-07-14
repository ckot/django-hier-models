from copy import deepcopy
import pprint

from django.conf import settings
# from django.apps import apps
from django.contrib import admin

pp = pprint.PrettyPrinter(indent=4)

DEFAULT_SETTINGS = {
    "top_level_models": {
        "exclude": [],
        "sort": False,
        "order": []
    },
    "use_hier_breadcrumbs": False
}


def disp_settings():
    tmp = deepcopy(settings.HIER_MODELS)
    app_labels = {mdl._meta.app_label for mdl in admin.site._registry}
    for app in app_labels:
        # add default settings for apps not listed
        if app not in tmp:
            tmp[app] = DEFAULT_SETTINGS
        else:
            # fill in any missing fields for partially setup apps
            tlm = "top_level_models"
            if tlm not in tmp[app]:
                tmp[app][tlm] = DEFAULT_SETTINGS[tlm]
            if "exclude" not in tmp[app][tlm]:
                tmp[app][tlm]["exclude"] = DEFAULT_SETTINGS[tlm]["exclude"]
            if "sort" not in tmp[app][tlm]:
                tmp[app][tlm]["sort"] = DEFAULT_SETTINGS[tlm]["sort"]
            if "order" not in tmp[app][tlm]:
                tmp[app][tlm]["order"] = DEFAULT_SETTINGS[tlm]["order"]
            if "use_hier_breadcrumbs" not in tmp[app]:
                tmp[app]["use_hier_breadcrumbs"] = \
                    DEFAULT_SETTINGS["use_hier_breadcrumbs"]

    pp.pprint(tmp)
