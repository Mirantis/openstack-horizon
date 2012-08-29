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
from horizon import tables

from ..tables import SubLBLinkAction


LOG = logging.getLogger(__name__)


class EditNode(SubLBLinkAction):
    name = 'edit'
    verbose_name = _('Edit Node')
    url = 'horizon:nova:load_balancer:nodes:update'
    classes = ('ajax-modal', 'btn-edit')


class DeleteNode(tables.DeleteAction):
    data_type_singular = _('Node')
    data_type_plural = _('Nodes')

    def delete(self, request, node_id):
        api.node_delete(request, self.table.kwargs['lb_id'], node_id)


class NodesTable(tables.DataTable):
    def link_callback(self, datum):
        lb_id = self.kwargs['lb_id']
        obj_id = self.get_object_id(datum)
        return urlresolvers.reverse('horizon:nova:load_balancer:nodes:detail',
                                    args=(lb_id, obj_id))

    STATUS_CHOICES = (
        ('inservice', True),
        ('', None),
        ('outservice', False),
    )
    id = tables.Column('id', hidden=True)
    name = tables.Column('name', verbose_name=_('Name'))
    address = tables.Column('address', verbose_name=_('Address'))
    port = tables.Column('port', verbose_name=_('Port'))
    weight = tables.Column('weight', verbose_name=_('Weight'))
    type = tables.Column('type', verbose_name=_('Type'))
    status = tables.Column('status', verbose_name=_('Status'),
                           status=True,
                           status_choices=STATUS_CHOICES)
    condition = tables.Column('condition', verbose_name=_('Condition'),
                              status=True)

    def __init__(self, *args, **kwargs):
        super(NodesTable, self).__init__(*args, **kwargs)
        # NOTE(akscram): Set callable link to reverse URL with two
        #                arguments.
        self.columns['name'].link = self.link_callback

    class Meta:
        name = 'nodes'
        verbose_name = _('Nodes')
        status_columns = ['status', 'condition']
        row_actions = (EditNode, DeleteNode)
        table_actions = (DeleteNode,)
