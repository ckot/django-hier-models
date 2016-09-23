"""
inspired by:

https://djangosnippets.org/snippets/2613/

"""
from __future__ import absolute_import
# from copy import deepcopy
import inspect
# import pprint

from django import template
from django.apps import apps
from django.conf import settings
from django.contrib.admin.templatetags.admin_modify \
    import submit_row as orig_submit_row
from django.core.urlresolvers import reverse
from django.utils.html import format_html

import hier_models.settings as hier_models_settings

# pp = pprint.PrettyPrinter(indent=4)
register = template.Library()

# hier_models_settings.disp_settings()


def get_app_hier_models_settings(app_label):
    """ returns either settings.HIER_MODELS[app_label] or default settings
    """
    # print "get_app_hier_models_settings(%s)" % app_label
    # default_settings = {
    #     "models_whitelist": ["*"],
    #     "models_blacklist": None,
    #     "use_hier_breadcrumbs": False,
    # }
    return settings.HIER_MODELS.get(app_label, None)
    # if tmp is not None:
    #     return tmp
    #     # overridden = deepcopy(default_settings)
    #     # # print "found HIER_MODELS[%s]" % app_label
    #     # # update default_settings, allowing for partial overrides
    #     # tlm = tmp.pop("top_level_models", None)
    #     # if tlm is not None:
    #     #     # print "top_level_models:"
    #     #     # pp.pprint(tlm)
    #     #     for key in tlm:
    #     #         # print "%s: %s\n" % (key, tlm[key])
    #     #         overridden["top_level_models"][key] = tlm[key]
    #     #     # print "end_top_level_models"
    #     #     # pp.pprint(defaults)
    #     # for key in tmp:
    #     #     overridden[key] = tmp[key]
    #     # pp.pprint(overridden)
    #     # return overridden
    # else:
    #     return default_settings

# can't override submit_row until I make changes so that this app
# can be added AFTER admin in INSTALLED app
@register.inclusion_tag('admin/submit_line.html', takes_context=True)
def hier_submit_row(context):
    ctx = orig_submit_row(context)
    ctx.update({
        'show_save_and_add_another': context.get(
            'show_save_and_add_another', ctx['show_save_and_add_another'])
    })
    return ctx


def filter_app_def_models(app_def):
    """ returns list of apps models, possibly with some excluded, or sorted
    """
    app_label = app_def['app_label']
    # print "filter_app_def_models:%s" % app_label
    all_models = app_def["models"]

    hm_settings = get_app_hier_models_settings(app_label)
    # pp.pprint(hier_models_settings)
    keep = all_models

    if hm_settings is not None:
        if hm_settings["whitelist_models"] is not None and \
            hm_settings["blacklist_models"] is not None:
            # nonsense - keep all models
            pass
        elif hm_settings["whitelist_models"] is None and \
            hm_settings["blacklist_models"] is None:
            # nonsense - keep all models
            pass
        elif hm_settings["whitelist_models"] is not None:
            if "*" in hm_settings["whitelist_models"]:
                # keep all models
                pass
            else:
                wl = hm_settings["whitelist_models"]
                keep = [mdl for mdl in all_models if mdl['object_name'] in wl]
        elif hm_settings["blacklist_models"] is not None:
            bl = hm_settings["blacklist_models"]
            keep = [mdl for mdl in all_models if mdl['object_name'] not in bl]
        # excludes = hm_settings['top_level_models']['exclude']
    # sort_models = hm_settings['top_level_models']['sort']
    # ordering = hm_settings['top_level_models']['order']
    # app_def_models = app_def['models']
    # keep = filter(lambda x: x['object_name'] not in excludes,
    #               app_def_models)
    # keep = [mdl for mdl in app_def_models if mdl['object_name'] not in excludes]
    # if sort_models and ordering:
    #     keep_dct = {model['object_name']: model for model in keep}
    #     ordered = [keep_dct[model_name] for model_name in ordering]
    # else:
    #     ordered = keep
    app_def['models'] = keep

@register.filter
def top_level_apps(app_list):
    for app_def in app_list:
        filter_app_def_models(app_def)
    return app_list


@register.filter
def top_level_models(app_models, app_def):
    filter_app_def_models(app_def)
    return app_def['models']


@register.assignment_tag(takes_context=True)
def use_hier_breadcrumbs(context):
    """returns boolean regarding whether the current app's settings request
    hierarchical breadcrumbs ('use_hier_breadcrumbs')
    """
    app_label = None
    use_hier = False
    for ctx in context:
        if 'app_label' in ctx:
            app_label = ctx['app_label']
    if app_label:
        hm_settings = get_app_hier_models_settings(app_label)
        if hm_settings:
            use_hier = hm_settings.get("use_hier_breadcrumbs", False)
    return use_hier


@register.assignment_tag(takes_context=True)
def get_hier_breadcrumbs(context):
    """returns list of breadcrumbs from a top-level model class's change-list
    all the way down to the instance (original)
    """
    original, app_label, model_name = None, None, None
    breadcrumbs, parents = [], []
    # initialize the above originally null values with what values contained
    # in context
    for ctx in context:
        if "opts" in ctx:
            model_name = ctx["opts"].verbose_name_plural.title()
        if 'app_label' in ctx:
            app_label = ctx['app_label']
        if 'original' in ctx:
            original = ctx["original"]
    if original is None:
        # this is a model, not an instance
        breadcrumbs.append(model_name)
        # print "original is None, returning breadcrumbs %s" % breadcrumbs
        return breadcrumbs

    if hasattr(original, 'parent'):
        # isn't a top-level model, trace the parent links until you find
        # a top-level model
        # print "original has parent"
        parent = original.parent
        prev = parent
        while parent is not None:
            parents.insert(0, parent)
            # print "parents: %s" % parents
            prev = parent
            if hasattr(parent, 'parent'):
                parent = parent.parent
            else:
                # hit a top level model (no parent property)
                # insert prev model's class instead of an instance
                # and break the loop
                parents.insert(0, prev.__class__)
                # print "hit top-level model, breaking loop: %s" % parents
                parent = None
    else:
        # no parent property, is a top-level model,
        # add link to class's changelist
        # print "original doesn't have parent property"
        kls = original.__class__
        url = reverse("admin:%s_%s_changelist" %
                      (app_label, kls._meta.model_name))
        breadcrumbs.append(
            format_html('<a href="%s">%s</a>' %
                        (url,
                         kls._meta.verbose_name_plural.title())))
    if len(parents):
        for parent in parents:
            link = None
            if inspect.isclass(parent):
                url = reverse("admin:%s_%s_changelist" %
                              (parent._meta.app_label,
                               parent._meta.model_name))
                link = format_html('<a href="%s">%s</a>' %
                                   (url,
                                    parent._meta.verbose_name_plural.title()))
            else:
                kls_meta = parent.__class__._meta
                kls_model_name = kls_meta.model_name
                kls_object_name = kls_meta.object_name
                kls_app_label = kls_meta.app_label
                url = reverse("admin:%s_%s_change" %
                              (kls_app_label, kls_model_name),
                              args=(parent.id,))
                link = format_html('<a href="%s">%s:%s</a>' %
                                   (url, kls_object_name, str(parent)))
            breadcrumbs.append(link)
    # this template tag is only used on change_forms, so we always have an
    # instance.  append the instances's class name: object_name
    breadcrumbs.append("%s:%s" %
                       (original.__class__.__name__, str(original)))
    return breadcrumbs


# do I need the following tag???

@register.simple_tag
def app_verbose_name(app_label):
    return apps.get_app_config(app_label).verbose_name

# don't think this is necessary anymore
#
# @register.assignment_tag
# def hm_app_is_installed(app_label):
#     """returns boolean regarding whether an app labeled app_label is
#     installed
#     """
#     return apps.is_installed(app_label)


# these are project-specific and should go away
#
# @register.filter
# def list_models_in_navbar_menu(app_def):
#     """returns boolean regarding whether the current app's settings request
#     the listing of it's models in the navbar menu ('models_in_navbar_menu')
#     """
#     list_models = True
#     app_label = app_def['app_label']
#     app_hier_models_settings = get_app_hier_models_settings(app_label)
#     list_models = app_hier_models_settings["models_in_navbar_menu"]
#     return list_models


# @register.filter
# def list_models_on_admin_index(app_def):
#     """returns boolean regarding whether the current app's settings request
#     the listing of it's models on the admin index page
#     ('models_on_admin_index')
#     """
#     list_models = True
#     app_label = app_def['app_label']
#     app_hier_models_settings = get_app_hier_models_settings(app_label)
#     list_models = app_hier_models_settings["models_on_admin_index"]
#     return list_models

