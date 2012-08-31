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

from django import shortcuts
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.forms.formsets import formset_factory
from django.contrib import messages
from django.views import generic
from django import http

from horizon import api
from horizon import exceptions
from horizon import tables
from horizon import forms

from .tables import LoadBalancersTable, LBTable
from .forms import CreateLoadBalancer, UpdateLoadBalancer
from .nodes.tables import NodesTable
from .nodes.forms import BaseNodeFormSet, CreateNode
from .nodes.views import NodeModalFormMixin
from .probes.tables import ProbesTable
from .vips.tables import VIPTable

from balancerclient.common import exceptions as balancerclient_exceptions
from novaclient import exceptions as novaclient_exceptions


LOG = logging.getLogger(__name__)


class LBFormMixin(object):
    client_error_redirect_url = None

    def get_algorithms(self):
        try:
            return [(algo, algo) for algo in api.algorithms_get(self.request)]
        except balancerclient_exceptions.ClientException, e:
            LOG.exception("balancerclient.ClientException: %r" % (e,))
            redirect = reverse(self.client_error_redirect_url)
            exceptions.handle(self.request,
                              _('Unable to retrieve list of algorithms'),
                              redirect=redirect)

    def get_protocols(self):
        try:
            return [(proto, proto) for proto in
                    api.protocols_get(self.request)]
        except balancerclient_exceptions.ClientException, e:
            LOG.exception("balancerclient.ClientException: %r" % (e,))
            redirect = reverse(self.client_error_redirect_url)
            exceptions.handle(self.request,
                              _('Unable to retrieve list of protocols'),
                              redirect=redirect)


class IndexView(tables.DataTableView):
    table_class = LoadBalancersTable
    template_name = 'nova/load_balancer/index.html'

    def get_data(self):
        try:
            lbs = api.lb_list(self.request)
        except:
            lbs = []
            exceptions.handle(self.request,
                    _('Unable to retrieve load balancers information.'))
        return lbs


class CreateView(forms.ModalFormView, LBFormMixin):
    form_class = CreateLoadBalancer
    template_name = 'nova/load_balancer/create.html'

    def get_form_kwargs(self):
        kwargs = super(CreateView, self).get_form_kwargs()
        kwargs['lb_algoritms'] = self.get_algorithms()
        kwargs['lb_protocols'] = self.get_protocols()
        return kwargs

    def get_initial(self):
        return {'vip_mask': '255.255.255.255'}


class UpdateView(forms.ModalFormView, LBFormMixin):
    form_class = UpdateLoadBalancer
    template_name = 'nova/load_balancer/update.html'
    context_object_name = 'lb'

    def get_form_kwargs(self):
        kwargs = super(UpdateView, self).get_form_kwargs()
        kwargs['lb_algoritms'] = self.get_algorithms()
        kwargs['lb_protocols'] = self.get_protocols()
        return kwargs

    def get_object(self, *args, **kwargs):
        if not hasattr(self, 'object'):
            lb_id = self.kwargs['lb_id']
            try:
                self.object = api.lb_get(self.request, lb_id)
            except balancerclient_exceptions.ClientException, e:
                redirect = reverse("horizon:nova:load_balancer:index")
                msg = _('Unable to retrieve Load Balancer details.')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self.object

    def get_initial(self):
        return {'lb': self.kwargs['lb_id'],
                'name': self.object.name,
                'algorithm': self.object.algorithm,
                'protocol': self.object.protocol,
                'port': getattr(self.object, 'port', '')}


class DetailView(tables.MultiTableView):
    table_classes = (VIPTable, NodesTable, ProbesTable, LBTable)
    template_name = 'nova/load_balancer/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['lb'] = self.get_lb()
        return context

    def get_lb(self):
        lb_id = self.kwargs['lb_id']
        try:
            return api.lb_get(self.request, lb_id)
        except balancerclient_exceptions.ClientException:
            redirect = reverse('horizon:nova:load_balancer:index')
            msg = _("Unable to retrieve details for Load balancer \"%s\".") % \
                  (lb_id,)
            exceptions.handle(self.request, msg, redirect=redirect)

    def get_lb_data(self):
        return [self.get_lb()]

    def get_nodes_data(self):
        try:
            nodes = api.node_list(self.request, self.kwargs['lb_id'])
        except balancerclient_exceptions.ClientException, e:
            nodes = []
            msg = _("Unable to fetch nodes: %s") % (e,)
            exceptions.handle(self.request, msg)
        return nodes

    def get_probes_data(self):
        try:
            probes = api.probe_list(self.request, self.kwargs['lb_id'])
        except balancerclient_exceptions.ClientException, e:
            probes = []
            msg = _("Unable to fetch probes: %s") % e
            exceptions.handle(self.request, msg)
        return probes

    def get_vips_data(self):
        try:
            vips = api.vip_list(self.request, self.kwargs['lb_id'])
        except balancerclient_exceptions.ClientException, e:
            vips = []
            msg = _("Unable to fetch Virtual IPs: %s") % e
            exceptions.handle(self.request, msg)
        return vips


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


class LoadBalancingView(NodeModalFormMixin, generic.TemplateView, LBFormMixin):
    template_name = 'nova/load_balancer/loadbalancing.html'

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

    def get_instances(self, ids):
        return [self.get_instance(instance_id) for instance_id in ids]

    def get_initial(self):
        return {'vip_mask': '255.255.255.255'}

    def get_nodes_initial(self, instances):
        return [self.get_node_initial(instance) for instance in instances]

    def get_node_initial(self, instance):
        return {'instance': instance,
                'instance_id': instance.id,
                'name': getattr(instance, 'name', ''),
                'weight': 10}

    def create_lb(self, request, data):
        try:
            # NOTE(akscram): The Port is a load balancing port and
            #                specified to LB and VIP.
            lb = api.lb_create(request, data['name'], data['algorithm'],
                               data['protocol'])
            messages.success(request, (_('Created Load Balancer "%s"') %
                                       (data['name'],)))
        except balancerclient_exceptions.ClientException, e:
            redirect = urlresolvers.reverse(
                               "horizon:nova:instances_and_volumes")
            exceptions.handle(request,
                              _("Error Creating Load Balancer: %r") % (e,),
                              redirect=redirect)
        else:
            if data['vip_address']:
                try:
                    # NOTE(akscram): Virtual IP created with empty name.
                    api.vip_create(request, lb.id, '', data['vip_address'],
                                   data['vip_mask'], data['port'],
                                   vlan=data['vip_vlan'])
                    messages.success(request, ("Created Virtual IP \"%s\"" %
                                               (data["vip_address"],)))
                except balancerclient_exceptions.ClientException, e:
                    LOG.exception("ClientException in CreateLoadBalancer")
                    messages.error(request,
                                   _("Error Creating Virtual IP: %s") % \
                                   e.message)
                finally:
                    return lb
            else:
                return lb

    def create_node(self, request, data):
        try:
            # NOTE(akscram): hardcoded NOVA_INSTANCE for horizon.
            api.node_create(request, data['lb'], data['name'], 'NOVA_INSTANCE',
                            data['address'], data['port'], data['weight'],
                            data['condition'],
                            instance_id=data['instance_id'])
            messages.info(request, _('Created node "%s"') % (data['name'],))
        except balancerclient_exceptions.ClientException, e:
            exceptions.handle(request, _("Error to create node: %r") % (e,))

    def get_form_kwargs(self):
        kwargs = super(CreateView, self).get_form_kwargs()
        kwargs['lb_algoritms'] = self.get_algorithms()
        kwargs['lb_protocols'] = self.get_protocols()
        return kwargs

    def get(self, request, *args, **kwargs):
        # NOTE(akscram): AJAX send IDs of checked instances.
        instances = self.get_instances(request.GET.getlist('instances[]'))
        if not instances:
            messages.error(request, _('Select nodes to load balancing.'))
            return shortcuts.redirect(reverse(
                                       "horizon:nova:instances_and_volumes"))
        NodeFormSet = formset_factory(CreateNode, formset=BaseNodeFormSet,
                                      extra=0)
        if request.method == 'POST':
            lb_form = CreateLoadBalancer(request.POST, request.FILES,
                                         initial=self.get_initial())
            lb_form.fields['algorithm'].choices = self.get_algorithms()
            lb_form.fields['protocol'].choices = self.get_protocols()
            node_formset = NodeFormSet(request.POST, request.FILES,
                               initial=self.get_nodes_initial(instances))
            if lb_form.is_valid() and node_formset.is_valid():
                lb = self.create_lb(request, lb_form.cleaned_data)
                for node_data in node_formset.cleaned_data:
                    node_data = node_data.copy()
                    node_data['lb'] = lb
                    self.create_node(request, node_data)
                handled = shortcuts.redirect(
                                  "horizon:nova:load_balancer:detail",
                                  lb_id=lb.id)
                if self.request.is_ajax():
                    # TODO(gabriel): This is not a long-term solution to how
                    # AJAX should be handled, but it's an expedient solution
                    # until the blueprint for AJAX handling is architected
                    # and implemented.
                    response = http.HttpResponse()
                    response['X-Horizon-Location'] = handled['location']
                    return response
                return handled
        else:
            lb_form = CreateLoadBalancer(initial=self.get_initial())
            lb_form.fields['algorithm'].choices = self.get_algorithms()
            lb_form.fields['protocol'].choices = self.get_protocols()
            node_formset = NodeFormSet(
                               initial=self.get_nodes_initial(instances))
        context = self.get_context_data(**kwargs)
        context['lb_form'] = lb_form
        context['node_formset'] = node_formset
        context['action_url'] = request.get_full_path()
        if self.request.is_ajax():
            context['hide'] = True
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
