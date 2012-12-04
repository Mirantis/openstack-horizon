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

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from horizon import exceptions
from horizon import tables

from openstack_dashboard import api


LOG = logging.getLogger(__name__)

class DeleteVip(tables.DeleteAction):
    data_type_singular = _("Vip")
    data_type_plural = _("Vips")

    def delete(self, request, vip_id):
        try:
            api.quantum_lb.vip_delete(request, vip_id)
            LOG.debug('Deleted network %s successfully' % vip_id)
        except:
            msg = _('Failed to delete network %s') % vip_id
            LOG.info(msg)
            redirect = reverse("horizon:project:loadbalancer:index")
            exceptions.handle(request, msg, redirect=redirect)


class VipsTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Name"),
                         link='horizon:project:loadbalancer:vips:detail')
    address = tables.Column("address", verbose_name=_("VIP Address"))
    port = tables.Column("port", verbose_name=_("TCP Port"))

    class Meta:
        name = "vips"
        verbose_name = _("Vips")
        table_actions = (DeleteVip, )
        row_actions = (DeleteVip, )


class MembersTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Name"),
                         link='horizon:project:loadbalancer:vips:detail')
    address = tables.Column("address", verbose_name=_("VIP Address"))
    port = tables.Column("port", verbose_name=_("TCP Port"))

    class Meta:
        name = "members"
        verbose_name = _("Members")
