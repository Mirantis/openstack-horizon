# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 OpenStack LLC
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging
import os

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.views import generic
from django import http

from horizon import api
from horizon import exceptions
from horizon import tables
from horizon import forms

from .tables import LoadBalancersTable
from .forms import CreateLoadBalancer, UpdateLoadBalancer
from .nodes.tables import NodesTable
from .probes.tables import ProbesTable

from balancerclient.common import exceptions as balancerclient_exceptions


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = LoadBalancersTable
    template_name = 'nova/load_balancer/index.html'

    def get_data(self):
        LOG.debug("Retrieve loadbalancers list %r" % self.request)
        try:
            lbs = api.lb_list(self.request)
        except:
            lbs = []
            exceptions.handle(self.request,
                    _('Unable to retrieve load balancers information.'))
        return lbs


class CreateView(forms.ModalFormView):
    form_class = CreateLoadBalancer
    template_name = 'nova/load_balancer/create.html'


class UpdateView(forms.ModalFormView):
    form_class = UpdateLoadBalancer
    template_name = 'nova/load_balancer/update.html'
    context_object_name = 'lb'

    def get_object(self, *args, **kwargs):
        if not hasattr(self, 'object'):
            lb_id = self.kwargs['lb_id']
            try:
                self.object = api.lb_get(self.request, lb_id)
            except balancerclient_exceptions.ClientException, e:
                LOG.exception('ClientException in get lb')
                redirect = reverse("horizon:nova:load_balancer:index")
                msg = _('Unable to retrieve load balancer details.')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self.object

    def get_initial(self):
        return {'lb': self.kwargs['lb_id'],
                'name': self.object.name,
                'algorithm': self.object.algorithm,
                'protocol': self.object.protocol,
                'port': getattr(self.object, 'port', '')}


class DetailView(tables.MultiTableView):
    table_classes = (NodesTable, ProbesTable)
    template_name = 'nova/load_balancer/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['lb'] = self.get_lb()
        return context

    def get_lb(self):
        lb_id = self.kwargs['lb_id']
        try:
            return api.lb_get(self.request, lb_id)
        except balancerclient_exceptions.ClientException, e:
            LOG.exception('ClientException in get lb')
            redirect = reverse('horion:nova:load_balancer:index')
            exceptions.handle(self.request,
                              _("Unable to retrieve details for load "
                                "balancer \"%s\".") % lb_id,
                              redirect=redirect)

    def get_nodes_data(self):
        try:
            nodes = api.node_list(self.request, self.kwargs['lb_id'])
        except balancerclient_exceptions.ClientException, e:
            LOG.exception('ClientException in nodes list')
            nodes = []
            messages.error(self.request, _("Unable to fetch nodes: %s") % e)
        return nodes

    def get_probes_data(self):
        try:
            probes = api.probe_list(self.request, self.kwargs['lb_id'])
        except balancerclient_exceptions.ClientException, e:
            LOG.exception('ClientException in probes list')
            probes = []
            messages.error(self.request, _("Unable to fetch probes: %s") % e)
        return probes


class MultiTypeForm(generic.TemplateView):
    form_class = None
    form_list = None
    initial = {}
    initial_list = {}

    def get_template_names(self):
        if self.request.is_ajax():
            if not hasattr(self, 'ajax_template_name'):
                # Transform standard template name to ajax name (leading "_")
                bits = list(os.path.split(self.template_name))
                bits[1] = "".join(("_", bits[1]))
                self.ajax_template_name = os.path.join(*bits)
            template = self.ajax_template_name
        else:
            template = self.template_name
        return template

    def get_object(self, *args, **kwargs):
        return None

    def get_initial(self):
        return self.initial

    def get_initial_list(self):
        initial_list = {}
        for form_name in self.form_list.keys():
            func_name = "get_%s_data" % form_name.lower()
            init_func = getattr(self, func_name, None)
            if init_func is not None:
                initial_list[form_name] = init_func()
            else:
                initial_list[form_name] = self.initial_list.get(form_name)
        return initial_list

    def get_form(self, request, form_class, *args, **kwargs):
        if request.method != 'POST':
            return form_class(*args, **kwargs)
        if request.FILES:
            return form_class(data=request.POST, files=request.FILES,
                              *args, **kwargs)
        else:
            return form_class(data=request.POST, *args, **kwargs)

    def get_form_list(self, request, *args, **kwargs):
        initial_list = self.get_initial_list()
        forms = {}
        for name, form_class in self.form_list.items():
            forms[name] = self.get_form(request, form_class,
                                        prefix=name,
                                        initial=initial_list[name],
                                        *args, **kwargs)
        return forms

    def maybe_handle(self, request, **kwargs):
        form = self.get_form(request, self.form_class,
                             initial=self.get_initial())
        forms = self.get_form_list(request)
        if request.method == 'POST' and form.is_valid():
            data = form.cleaned_data.copy()
            type_form = forms[data['type']]
            if type_form.is_valid():
                data.update(type_form.cleaned_data)
                try:
                    return form, forms, self.handle(request, data)
                except Exception:
                    exceptions.handle(request)
                    return form, forms, None
        return form, forms, None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(*args, **kwargs)
        form, forms, handled = self.maybe_handle(request, **kwargs)
        if handled:
            if self.request.is_ajax():
                # TODO(gabriel): This is not a long-term solution to how
                # AJAX should be handled, but it's an expedient solution
                # until the blueprint for AJAX handling is architected
                # and implemented.
                response = http.HttpResponse()
                response['X-Horizon-Location'] = handled['location']
                return response
            return handled
        context = self.get_context_data(**kwargs)
        context.update({'object': self.object,
                        'form': form,
                        'forms': forms})
        if self.request.is_ajax():
            context['hide'] = True
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """ Placeholder to allow POST; handled the same as GET. """
        return self.get(request, *args, **kwargs)

    def handle(self, request, data):
        raise NotImplementedError
