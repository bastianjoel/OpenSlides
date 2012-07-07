#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    openslides.utils.views
    ~~~~~~~~~~~~~~~~~~~~~~

    Views for OpenSlides.

    :copyright: 2011, 2012 by OpenSlides team, see AUTHORS.
    :license: GNU GPL, see LICENSE for more details.
"""

try:
    import json
except ImportError:
    # for python 2.5 support
    import simplejson as json

try:
    from cStringIO import StringIO
except ImportError:
    # Is this exception realy necessary?
    from StringIO import StringIO

from reportlab.platypus import (SimpleDocTemplate, Paragraph, Frame, PageBreak,
    Spacer, Table, LongTable, TableStyle, Image)
from reportlab.lib.units import cm

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.conf import settings
from django.dispatch import receiver
from django.http import HttpResponseServerError, HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.utils.importlib import import_module
from django.template import loader, RequestContext
from django.template.loader import render_to_string
from django.views.generic import (
    TemplateView as _TemplateView,
    RedirectView as _RedirectView,
    UpdateView as _UpdateView,
    CreateView as _CreateView,
    View as _View,
    FormView as _FormView,
    ListView as _ListView,
)
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import TemplateResponseMixin

from openslides.config.models import config

from openslides.utils.utils import render_to_forbitten, html_strong
from openslides.utils.signals import template_manipulation
from openslides.utils.pdf import firstPage, laterPages


NO_PERMISSION_REQUIRED = 'No permission required'

View = _View


class SetCookieMixin(object):
    def render_to_response(self, context, **response_kwargs):
        response = TemplateResponseMixin.render_to_response(self, context, **response_kwargs)
        if 'cookie' in context:
            response.set_cookie(context['cookie'][0], context['cookie'][1])
        return response


class LoginMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginMixin, self).dispatch(request, *args, **kwargs)


class PermissionMixin(object):
    permission_required = NO_PERMISSION_REQUIRED

    def has_permission(self, request):
        if self.permission_required == NO_PERMISSION_REQUIRED:
            return True
        else:
            return request.user.has_perm(self.permission_required)

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission(request):
            if not request.user.is_authenticated():
                path = request.get_full_path()
                return HttpResponseRedirect("%s?next=%s" % (settings.LOGIN_URL, path))
            else:
                return render_to_forbitten(request)
        return _View.dispatch(self, request, *args, **kwargs)


class AjaxMixin(object):
    def get_ajax_context(self, **kwargs):
        return {}

    def ajax_get(self, request, *args, **kwargs):
        return HttpResponse(json.dumps(self.get_ajax_context(**kwargs)))


class TemplateView(PermissionMixin, _TemplateView):
    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        template_manipulation.send(sender=self.__class__, request=self.request, context=context)
        return context


class ListView(PermissionMixin, SetCookieMixin, _ListView):
    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        template_manipulation.send(sender=self.__class__, request=self.request, context=context)
        return context


class AjaxView(PermissionMixin, AjaxMixin, View):
    def get(self, request, *args, **kwargs):
        return self.ajax_get(request, *args, **kwargs)


class RedirectView(PermissionMixin, AjaxMixin, _RedirectView):
    permanent = False
    allow_ajax = False

    def pre_redirect(self, request, *args, **kwargs):
        pass

    def pre_post_redirect(self, request, *args, **kwargs):
        pass

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            self.pre_redirect(request, *args, **kwargs)
        elif request.method == 'POST':
            self.pre_post_redirect(request, *args, **kwargs)

        if self.request.is_ajax() and self.allow_ajax:
            return self.ajax_get(request, *args, **kwargs)
        return super(RedirectView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, **kwargs):
        return reverse(super(RedirectView, self).get_redirect_url(**kwargs))


class FormView(PermissionMixin, _FormView):
    def get_success_url(self):
        if not self.success_url:
            return ''
        return reverse(super(FormView, self).get_success_url())

    def get_context_data(self, **kwargs):
        context = super(FormView, self).get_context_data(**kwargs)
        template_manipulation.send(sender=self.__class__, request=self.request, context=context)
        return context

    def form_invalid(self, form):
        messages.error(self.request, _('Please check the form for errors.'))
        return super(FormView, self).form_invalid(form)


class UpdateView(PermissionMixin, _UpdateView):
    def get_success_url(self):
        messages.success(self.request, self.get_success_message())
        if 'apply' in self.request.POST:
            return ''
        return reverse(super(UpdateView, self).get_success_url())

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        template_manipulation.send(sender=self.__class__, request=self.request, context=context)
        return context

    def form_invalid(self, form):
        messages.error(self.request, _('Please check the form for errors.'))
        return super(UpdateView, self).form_invalid(form)

    def get_success_message(self):
        return _('%s was successfully modified.') % html_strong(self.object)


class CreateView(PermissionMixin, _CreateView):
    def get_success_url(self):
        messages.success(self.request, self.get_success_message())
        if 'apply' in self.request.POST:
            return reverse(self.get_apply_url(), args=[self.object.id])
        return reverse(super(CreateView, self).get_success_url())

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        template_manipulation.send(sender=self.__class__, request=self.request, context=context)
        return context

    def get_apply_url(self):
        #todo: Versuche apply url automatisch anhand on self.object herauszufindne
        return self.apply_url

    def form_invalid(self, form):
        messages.error(self.request, _('Please check the form for errors.'))
        return super(CreateView, self).form_invalid(form)

    def get_success_message(self):
        return _('%s was successfully created.') % html_strong(self.object)


class DeleteView(RedirectView, SingleObjectMixin):
    def get_confirm_question(self):
        return _('Do you really want to delete %s?') % html_strong(self.object)

    def get_success_message(self):
        return  _('%s was successfully deleted.') % html_strong(self.object)

    def pre_redirect(self, request, *args, **kwargs):
        self.confirm_form(request, self.object)

    def pre_post_redirect(self, request, *args, **kwargs):
        self.object.delete()
        messages.success(request, self.get_success_message())

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(DeleteView, self).get(request, *args, **kwargs)

    def confirm_form(self, request, object):
        self.gen_confirm_form(request, self.get_confirm_question(), object.get_absolute_url('delete'))

    def gen_confirm_form(self, request, message, url):
        messages.warning(request, '%s<form action="%s" method="post"><input type="hidden" value="%s" name="csrfmiddlewaretoken"><input type="submit" value="%s" /> <input type="button" value="%s"></form>' % (message, url, csrf(request)['csrf_token'], _("Yes"), _("No")))


class DetailView(TemplateView, SingleObjectMixin):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return super(DetailView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context.update(SingleObjectMixin.get_context_data(self, **kwargs))
        return context


class PDFView(PermissionMixin, View):
    filename = _('undefined-filename')
    top_space = 3
    document_title = None

    def get_top_space(self):
        return self.top_space

    def get_document_title(self):
        return self.document_title

    def get_filename(self):
        return self.filename

    def get_template(self, buffer):
        return SimpleDocTemplate(buffer)

    def build_document(self, pdf_document, story):
        pdf_document.build(story, onFirstPage=firstPage, onLaterPages=laterPages)

    def render_to_response(self, filename):
        response = HttpResponse(mimetype='application/pdf')
        filename = u'filename=%s.pdf;' % self.get_filename()
        response['Content-Disposition'] = filename.encode('utf-8')

        buffer = StringIO()
        pdf_document = self.get_template(buffer)
        pdf_document.title = self.get_document_title()
        story = [Spacer(1, self.get_top_space()*cm)]

        self.append_to_pdf(story)

        self.build_document(pdf_document, story)

        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    def append_to_pdf(self, story):
        pass

    def get_filename(self):
        return self.filename

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_filename())


class FrontPage(TemplateView):
    template_name = 'front_page.html'

    def has_permission(self, request):
        if request.user.is_authenticated() or config['system_enable_anonymous']:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(FrontPage, self).get_context_data(**kwargs)
        apps = []
        for app in settings.INSTALLED_APPS:
            try:
                mod = import_module(app + '.views')
                tab = mod.register_tab(self.request)
            except (ImportError, AttributeError):
                continue
            if tab.permission:
                apps.append(tab)
        if config['show_help_text']:
            messages.info(self.request, config['help_text'])
        context.update({
            'apps': apps,
            'title': config['frontpage_title'],
            'welcometext': config['frontpage_welcometext'],
        })
        return context


def server_error(request, template_name='500.html'):
    """
    500 error handler.

    Templates: `500.html`
    Context:
        MEDIA_URL
            Path of static media (e.g. "media.example.org")
    """
    t = loader.get_template("500.html") # You need to create a 500.html template.
    return HttpResponseServerError(render_to_string('500.html', context_instance=RequestContext(request)))


@receiver(template_manipulation, dispatch_uid="send_register_tab")
def send_register_tab(sender, request, context, **kwargs):
    tabs = []
    for app in settings.INSTALLED_APPS:
        try:
            mod = import_module(app + '.views')
            tabs.append(mod.register_tab(request))
        except (ImportError, AttributeError):
            continue

    context.update({
        'tabs': tabs,
    })
