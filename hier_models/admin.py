from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


class TopLevelModelMixin(object):

    def get_next_url(self, request, obj):
        """ returns the url to go to next after the admin form is saved

        The behavior regarding where to go next regarding whether the origin
        was a add or change form is the same so the logic was simply moved
        here to keep things DRY
        """
        cm = obj.__class__._meta
        url = reverse("admin:app_list", args=(cm.app_label, ))
        if '_continue' in request.POST:
            url = reverse("admin:%s_%s_change" % (cm.app_label, cm.model_name),
                          args=(obj.pk, ))
        elif '_addanother' in request.POST:
            url = reverse("admin:%s_%s_add" % (cm.app_label, cm.model_name))
        return url

    def response_add(self, request, obj, post_url_continue=None):
        return HttpResponseRedirect(self.get_next_url(request, obj))

    def response_change(self, request, obj):
        return HttpResponseRedirect(self.get_next_url(request, obj))


class NonTopLevelModelMixin(object):
    """
    This class overrides the behavior of the 'Save and add another',
    and 'Save' buttons on admin add/change forms


    In order for any of this to work, you will need to declare a property
    called 'parent' on your models which returns the foreign key to the
    next object up in the hierarchy. If no 'parent' attribute is found, the
    next url after clicking 'Save' or 'Save and add another' will simply take
    you to your app's app_list in the admin.  Provided you've declared your
    'parent' properties:

    'Save' will take you to the 'parent' object in the hierarchy
    'Save and add another' will do the same.


    Furthermore the 'Save and add another' button isn't displayed by default
    but if you override the change_form.html template you must replace
    the 'submit_row' template tag with 'hier_submit_row', else, the button
    will still be displayed, but will have the behavior as described above
    """

    def get_parent_change_url(self, obj):
        # default in case there is no parent
        url = reverse("admin:app_list",
                      args=(obj.__class__._meta.app_label,))
        if hasattr(obj, "parent"):
            parent = obj.parent
            pcm = parent.__class__._meta
            url = reverse("admin:%s_%s_change" %
                          (pcm.app_label, pcm.model_name),
                          args=(parent.pk, ))
        return url

    def get_object_change_url(self, obj):
        cm = obj.__class__._meta
        return reverse("admin:%s_%s_change" % (cm.app_label, cm.model_name),
                       args=(obj.pk, ))

    def get_next_url(self, request, obj):
        """ returns the url to go to next after the admin form is saved

        The behavior regarding where to go next regarding whether the origin
        was a add or change form is the same so the logic was simply moved
        here to keep things DRY
        """
        if '_continue' in request.POST:
            url = self.get_object_change_url(obj)
        elif '_addanother' in request.POST:
            # normally this won't occur, but just in case change_form.html was
            # overridden and the 'submit_row' template tag didn't get replaced
            # with 'hier_submit_row' we'll send them to the parent if they
            # clicked 'Save and add another'
            url = self.get_parent_change_url(obj)
        else:
            url = self.get_parent_change_url(obj)
        return url

    def response_add(self, request, obj, post_url_continue=None):
        return HttpResponseRedirect(self.get_next_url(request, obj))

    def response_change(self, request, obj):
        return HttpResponseRedirect(self.get_next_url(request, obj))

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """removes the 'Save and add another' button from the view

        requires that the 'submit_row' template tag in change_form.html gets
        replaced with 'hier_submit_row'
        """
        extra_context = extra_context or {}
        extra_context["show_save_and_add_another"] = False
        return super(NonTopLevelModelMixin, self).change_view(
            request, object_id, form_url=form_url, extra_context=extra_context)
