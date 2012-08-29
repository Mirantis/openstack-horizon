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

from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import exceptions
from horizon import tables
from horizon import tabs
from horizon import forms

from .forms import AddNode, UpdateNode, NODE_NOVA_INSTANCE
from .tabs import NodeDetailTabs

from balancerclient.common import exceptions as balancerclient_exceptions


LOG = logging.getLogger(__name__)


class NodeModalFormMixin(object):
    client_error_redirect_url = None

    def get_node_lb_choices(self):
        try:
            return [(lb.id, lb.name) for lb in api.lb_list(self.request)]
        except balancerclient_exceptions.ClientException, e:
            LOG.exception("balancerclient.ClientException: %r" % (e,))
            redirect = urlresolvers.reverse(self.client_error_redirect_url)
            exceptions.handle(self.request,
                              _('Unable to retrieve list of load balancers'),
                              redirect=redirect)

    def get_node_address_choices(self, instance):
        choices = []
        for label, addresses in instance.addresses.items():
            for address in addresses:
                item_label = "%s [%s]" % (address['addr'], label)
                choices.append((address['addr'], item_label))
        return choices

    def get_instance(self, instance_id):
        try:
            return api.server_get(self.request, instance_id)
        except novaclient_exceptions.ClientException, e:
            redirect = urlresolvers.reverse(
                               "horizon:nova:instances_and_volumes:index")
            msg = _('Unable to get instance "%s".') % instance_id
            exceptions.handle(request, msg, redirect=redirect)


class AddView(NodeModalFormMixin, forms.ModalFormView):
    form_class = AddNode
    template_name = 'nova/load_balancer/nodes/add.html'
    client_error_redirect_url = 'horizon:nova:instances_and_volumes:index'

    def get_form_kwargs(self):
        kwargs = super(AddView, self).get_form_kwargs()
        kwargs['lb_choices'] = self.get_node_lb_choices()
        kwargs['address_choices'] = self.get_node_address_choices(self.object)
        return kwargs

    def get_object(self, *args, **kwargs):
        if not hasattr(self, "object"):
            self.object = self.get_instance(self.kwargs['instance_id'])
        return self.object

    def get_initial(self):
        return {'instance_id': self.kwargs['instance_id'],
                'name': getattr(self.object, 'name', ''),
                'weight': 10}


class UpdateView(NodeModalFormMixin, forms.ModalFormView):
    form_class = UpdateNode
    template_name = 'nova/load_balancer/nodes/update.html'
    context_object_name = 'node'

    def get_form_kwargs(self):
        kwargs = super(UpdateView, self).get_form_kwargs()
        # FIXME(akscram): Support only ondes created in Horizon.
        if self.object.type == NODE_NOVA_INSTANCE:
            instance = self.get_instance(self.object.instance_id)
            choices = self.get_node_address_choices(instance)
        else:
            choices = []
        kwargs['address_choices'] = choices
        return kwargs

    def get_object(self, *args, **kwargs):
        if not hasattr(self, 'object'):
            lb_id = self.kwargs['lb_id']
            node_id = self.kwargs['node_id']
            try:
                self.object = api.node_get(self.request, lb_id, node_id)
            except balancerclient_exceptions.ClientException, e:
                LOG.exception('ClientException in get node')
                redirect = urlresolvers.reverse(
                                'horizon:nova:load_balancer:detail',
                                kwargs={'lb_id': lb_id})
                msg = _('Unable to retrieve node details.')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self.object

    def get_initial(self):
        return {'lb_id': self.kwargs['lb_id'],
                'node_id': self.kwargs['node_id'],
                'name': self.object.name,
                'address': self.object.address,
                'port': self.object.port,
                'weight': self.object.weight,
                'condition': self.object.condition}


class DetailView(tabs.TabView):
    tab_group_class = NodeDetailTabs
    template_name = 'nova/load_balancer/nodes/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["node"] = self.get_data()
        return context

    def get_data(self):
        if not hasattr(self, "_node"):
            lb_id = self.kwargs['lb_id']
            node_id = self.kwargs['node_id']
            try:
                node = api.node_get(self.request, lb_id, node_id)
            except:
                redirect = urlresolvers.reverse(
                                   'horizon:nova:load_balancer:detail',
                                   args=(lb_id,))
                exceptions.handle(self.request,
                                  _('Unable to retrieve details for '
                                    'Node "%s".') % (node_id,),
                                    redirect=redirect)
            self._node = node
        return self._node

    def get_tabs(self, request, *args, **kwargs):
        node = self.get_data()
        return self.tab_group_class(request, node=node, **kwargs)
