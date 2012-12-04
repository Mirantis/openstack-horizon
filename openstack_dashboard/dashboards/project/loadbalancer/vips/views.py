# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
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

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables

from openstack_dashboard import api
from .members.tables import MembersTable


LOG = logging.getLogger(__name__)


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
        if not hasattr(self, "_vip"):
            try:
                vip_id = self.kwargs['vip_id']
                vip = api.quantum_lb.vip_get(self.request, vip_id)
                vip.set_id_as_name_if_empty(length=0)
            except:
                msg = _('Unable to retrieve details for vip "%s".')\
                      % (vip_id)
                exceptions.handle(self.request, msg, redirect=self.failure_url)
            self._network = vip
        return vip

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["vip"] = self._get_data()
        return context
