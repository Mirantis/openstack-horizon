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

from django.utils.translation import ugettext_lazy as _

from horizon import tabs
from horizon import exceptions
from openstack_dashboard import api
from .members.tables import MembersTable
from .vips.tables import VipsTable


class VipsTab(tabs.TableTab):
    table_classes = (VipsTable,)
    name = _("Vips")
    slug = "vips"
    template_name = "horizon/common/_detail_table.html"

    def get_vips_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            vips = api.quantum_lb.vip_list(self.request)
        except:
            vips = []
            msg = _('Vip list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for n in vips:
            n.set_id_as_name_if_empty()
        return vips


class MembersTab(tabs.TableTab):
    table_classes = (MembersTable,)
    name = _("Members")
    slug = "members"
    template_name = "horizon/common/_detail_table.html"

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


class HealthMonitorsTab(tabs.TableTab):
    table_classes = (MembersTable,)
    name = _("HealthMonitors")
    slug = "healthmonitors"
    template_name = "horizon/common/_detail_table.html"

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


class LoadBalancerTabs(tabs.TabGroup):
    slug = "loadbalancer"
    tabs = (VipsTab, MembersTab, HealthMonitorsTab, )
    sticky = True
