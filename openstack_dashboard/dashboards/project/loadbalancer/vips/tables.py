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


#class CheckServiceEditable(object):
#    """Mixin class to determine the specified service is editable."""
#
#    def allowed(self, request, datum=None):
#        # Only administrator is allowed to create and manage subnets
#        # on shared services.
#        service = self.table._get_service()
#        if service.shared:
#            return False
#        return True
#
#
#class DeleteSubnet(CheckServiceEditable, tables.DeleteAction):
#    data_type_singular = _("Subnet")
#    data_type_plural = _("Subnets")
#
#    def delete(self, request, obj_id):
#        try:
#            api.quantum.subnet_delete(request, obj_id)
#        except:
#            msg = _('Failed to delete subnet %s') % obj_id
#            LOG.info(msg)
#            service_id = self.table.kwargs['service_id']
#            redirect = reverse('horizon:project:services:detail',
#                               args=[service_id])
#            exceptions.handle(request, msg, redirect=redirect)
#
#
#class CreateSubnet(CheckServiceEditable, tables.LinkAction):
#    name = "create"
#    verbose_name = _("Create Subnet")
#    url = "horizon:project:services:addsubnet"
#    classes = ("ajax-modal", "btn-create")
#
#    def get_link_url(self, datum=None):
#        service_id = self.table.kwargs['service_id']
#        return reverse(self.url, args=(service_id,))
#
#
#class UpdateSubnet(CheckServiceEditable, tables.LinkAction):
#    name = "update"
#    verbose_name = _("Edit Subnet")
#    url = "horizon:project:services:editsubnet"
#    classes = ("ajax-modal", "btn-edit")
#
#    def get_link_url(self, subnet):
#        service_id = self.table.kwargs['service_id']
#        return reverse(self.url, args=(service_id, subnet.id))


class MembersTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Name"))
    address = tables.Column("address", verbose_name=_("Address"))
    port = tables.Column("port", verbose_name=_("TCP Port"))

    class Meta:
        name = "members"
        verbose_name = _("Members")

        table_actions = (DeleteMember, )
        row_actions = (DeleteMember, )
