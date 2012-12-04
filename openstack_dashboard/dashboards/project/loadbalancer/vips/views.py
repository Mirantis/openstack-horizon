# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 NEC Corporation
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

"""
Views for managing Quantum Subnets.
"""
import logging

from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import workflows

from openstack_dashboard import api
from .forms import CreateSubnet, UpdateSubnet
from .tables import MembersTable


LOG = logging.getLogger(__name__)


#class CreateView(forms.ModalFormView):
#    form_class = CreateSubnet
#    template_name = 'project/networks/subnets/create.html'
#    success_url = 'horizon:project:networks:detail'
#
#    def get_success_url(self):
#        return reverse(self.success_url,
#                       args=(self.kwargs['network_id'],))
#
#    def get_object(self):
#        if not hasattr(self, "_object"):
#            try:
#                network_id = self.kwargs["network_id"]
#                self._object = api.quantum.network_get(self.request,
#                                                       network_id)
#            except:
#                redirect = reverse('horizon:project:networks:index')
#                msg = _("Unable to retrieve network.")
#                exceptions.handle(self.request, msg, redirect=redirect)
#        return self._object
#
#    def get_context_data(self, **kwargs):
#        context = super(CreateView, self).get_context_data(**kwargs)
#        context['network'] = self.get_object()
#        return context
#
#    def get_initial(self):
#        network = self.get_object()
#        return {"network_id": self.kwargs['network_id'],
#                "network_name": network.name}
#
#
#class UpdateView(forms.ModalFormView):
#    form_class = UpdateSubnet
#    template_name = 'project/networks/subnets/update.html'
#    context_object_name = 'subnet'
#    success_url = reverse_lazy('horizon:project:networks:detail')
#
#    def get_success_url(self):
#        return reverse('horizon:project:networks:detail',
#                       args=(self.kwargs['network_id'],))
#
#    def _get_object(self, *args, **kwargs):
#        if not hasattr(self, "_object"):
#            subnet_id = self.kwargs['subnet_id']
#            try:
#                self._object = api.quantum.subnet_get(self.request, subnet_id)
#            except:
#                redirect = reverse("horizon:project:networks:index")
#                msg = _('Unable to retrieve subnet details')
#                exceptions.handle(self.request, msg, redirect=redirect)
#        return self._object
#
#    def get_context_data(self, **kwargs):
#        context = super(UpdateView, self).get_context_data(**kwargs)
#        subnet = self._get_object()
#        context['subnet_id'] = subnet.id
#        context['network_id'] = subnet.network_id
#        context['cidr'] = subnet.cidr
#        context['ip_version'] = subnet.ipver_str
#        return context
#
#    def get_initial(self):
#        subnet = self._get_object()
#        return {'network_id': self.kwargs['network_id'],
#                'subnet_id': subnet['id'],
#                'cidr': subnet['cidr'],
#                'ip_version': subnet['ip_version'],
#                'name': subnet['name'],
#                'gateway_ip': subnet['gateway_ip']}


class DetailView(tables.MultiTableView):
    table_classes = (MembersTable, )
    template_name = 'project/loadbalancer/vips/detail.html'
    failure_url = reverse_lazy('horizon:project:loadbalancer:index')

    def get_members_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            members = api.quantum_lb.member_list(self.request)
        except:
            members = []
            msg = _('Member list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for n in members:
            n.set_id_as_name_if_empty()
        return members

    def _get_data(self):
#        if not hasattr(self, "_network"):
#            try:
#                network_id = self.kwargs['network_id']
#                network = api.quantum.network_get(self.request, network_id)
#                network.set_id_as_name_if_empty(length=0)
#            except:
#                msg = _('Unable to retrieve details for network "%s".')\
#                      % (network_id)
#                exceptions.handle(self.request, msg, redirect=self.failure_url)
#            self._network = network
        return api.quantum_lb.vip_list(self.request)[0]

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["vip"] = self._get_data()
        return context
