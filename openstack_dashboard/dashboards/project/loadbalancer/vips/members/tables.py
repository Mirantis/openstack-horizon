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

from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables

from openstack_dashboard import api


LOG = logging.getLogger(__name__)


class DeleteMember(tables.DeleteAction):
    data_type_singular = _("Member")
    data_type_plural = _("Members")

    def delete(self, request, obj_id):
        try:
            api.quantum_lb.member_delete(request, obj_id)
        except:
            msg = _('Failed to delete member %s') % obj_id
            LOG.info(msg)
#            service_id = self.table.kwargs['service_id']
#            redirect = reverse('horizon:project:services:detail',
#                               args=[service_id])
#            exceptions.handle(request, msg, redirect=redirect)


class CreateMember(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Member")
    url = "horizon:project:loadbalancer:vips:addmember"
    classes = ("ajax-modal", "btn-create")

    def get_link_url(self, datum=None):
        vip_id = self.table.kwargs['vip_id']
        return reverse(self.url, args=(vip_id,))


class UpdateMember(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Member")
    url = "horizon:project:loadbalancer:vips:members:update"
    classes = ("ajax-modal", "btn-edit")

    def get_link_url(self, member):
        print self.url
        print self.table
        print member

        vip_id = self.table.kwargs['vip_id']
#        member_id = self.table.kwargs['member_id']

#        member_id = self.table.kwargs['member_id']
        return reverse(self.url, args=(vip_id,))
#        return reverse(self.url, args=(vip_id, member_id))


class MembersTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Name"))
    address = tables.Column("address", verbose_name=_("Address"))
    port = tables.Column("port", verbose_name=_("TCP Port"))

    class Meta:
        name = "members"
        verbose_name = _("Members")
        table_actions = (CreateMember, DeleteMember)
        row_actions = ( DeleteMember, )
