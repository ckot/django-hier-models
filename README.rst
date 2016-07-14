django-hier_models
==================

Installation
=============

::

    pip install django-hier-models



Configuration
=============

settings.py

::

    INSTALLED_APPS = [
        ...
        'hier_models',
        ...
    ]

    HIER_MODELS = {
        "<your app>": {
            "top_level_models": {
                'exclude': [] # list of models you don't want in app index
                'sort': True,
                'order': [] # if sort=True, order of non-excluded models (override default alphanum sorting)
            },
            "use_hier_breadcrumbs": True  # whether this app makes use of hierarchical breadcrumbs
        },
        '<some other app': {
            ...
        }
    }



Usage
=====

This package provides:

* A set of admin.modelAdmin subclasses
    + TopLevelModelAdmin()
    + NonTopLevelModelAdmin()
        + Any models making use of this you will need to define a 'parent'
          property which returns the id of whatever object is one level higher in the model hierarchy
* templatetags
    + get_hier_breadcrumbs
    + hier_submit_row
    + filter_app_def_models
