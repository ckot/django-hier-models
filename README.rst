django-hier_models
==================

A Django app which makes it easier to work with deeply nested models.

For instance, you may have a model hierarchy where you only wish be able to
create various models via an inline in it's parent in the hierarchy.  In this
case, you don't want all of your app's models listed on the admin's index or
on the app's app_index page.

Reasons for this is that foreign key fields may contain a huge list of options.

Granted, you can always make use of filters, and this app in no way precludes
you from doing that.

In addition to adding filtering capabiltity for what models get listed in the Admin's index page and your app's app_index page,

This is handled by the 'top_level_models' and 'top_level_apps' templatetags

A 'get_hier_breadcrumbs' templatetag is also provided, which will display the path all the way from the current instance all the way back
to the admin home page

A NonTopLevelModelAdmin  mixin is provided, which changes the behavior of the 'save' link so that it takes you back
to the parent objects (the one which contains the inline you created the current object on) change page.  It also disables (FIXME: I need to verify this) the 'save_and_add_another' link, as unfortunately, foreign key fields aren't allowed when setting a modelAdmin's default_values


KNOWN ISSUES:
=============

Due to this originally being developed as part of another project, and that I *currently* don't have any unit tests,
I've discovered that I have references to some things specific to that project, including:

examples/templates - reference to an external include.  This is currently being resolved.

settings.py - some project-specific settings. These are currently being removed.

templatetags/hier_models_tags.py - there are some templatetags related to project-specific settings.  These are being removed, but are otherwise harmless, as I don't document their usage.


Installation
=============

::

    Currently, this app isn't up on PyPi, so you will need to install as follows:

    pip install git+git://github.com/ckot/django-hier-models.git



Usage
=====

**models.py**

Each of your models which is *not* a top-level-model will need to provide a
'parent'  property, which returns the foreign key to whatever model's modeladmin
contains the inline this object is associated with

Your app will need to provide the following templates:


**templates/admin/index.html**

::

    You'll need to:
    Add:
        'hier_models_tags' to the {%load %} directive

    Change:
        'for app in app_list' to 'for app in app_list|top_level_apps'


**templates/admin/app_index.html**

::

    You'll need to:
        Add:
            'hier_models_tags' to the {%load %} directive

        Change:
            'for app in app_list' to 'for app in app_list|top_level_models'




**templates/admin/change_form.html**

::

    You'll need to replace the contents of {% block breadcrumbs %} with
    "include hier_models/hier_breadcrumbs.html"


And you will need to make the following changes in **settings.py**

::

    INSTALLED_APPS = [
        'your_app',  # needs to be before admin, as you will be overriding some admin templates
        ...
        'django.contrib.admin',
        ...
        'hier_models',
        ...
    ]

    HIER_MODELS = {
        # configure an app where list of models you wish to list is shorter
        # than the ones you don't
        "your app_label": {
            "whitelist_models": ["models", "you", "want", "listed", "everywhere"],
            "blacklist_models": None,
            "use_hier_breadcrumbs": True  # whether this app makes use of hierarchical breadcrumbs
        },
        # config for an app where the list of models you don't wish to list is
        # shorter the the ones you do
        'another_app_label': {
            "whitelist_models": None,
            "blacklist_models": ["models", "you", "don't", "want", "listed", "everywhere"],
            "use_hier_breadcrumbs": False
        },
        # config an app to only make use of hierarchical breadcrumbs
        'yet_another_app_label': {
            "whitelist_models": ["*"], # special value to whitelist all models
            "blacklist_models": None,
            "use_hier_breadcrumbs": True
        },
        # will act the same as "whitelist_models": "*" (support simply added to prevent errors)
        'and_another': {
            "whitelist_models": None,
            "blacklist_models": None,
            "use_hier_breadcrumbs": True
        },
        # non-sensical. not making use of this module for this app, might as well not
        # have an entry here
        'yet_another': {
            "whitelist_models": None,
            "blacklist_models": None,
            "use_hier_breadcrumbs": False
        }
    }

