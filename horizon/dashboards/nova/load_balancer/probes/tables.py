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


class CreateProbe(SubLBLinkAction):
    name = 'create'
    verbose_name = _('Create Probe')
    url = 'horizon:nova:load_balancer:probes:create'
    classes = ('ajax-modal', 'btn-create')


class DeleteProbe(tables.DeleteAction):
    data_type_singular = _('Probe')
    data_type_plural = _('Probes')

    def delete(self, request, probe_id):
        api.probe_delete(request, self.table.kwargs['lb_id'], probe_id)


class ProbesTable(tables.DataTable):
    def link_callback(self, datum):
        lb_id = self.kwargs['lb_id']
        obj_id = self.get_object_id(datum)
        return urlresolvers.reverse('horizon:nova:load_balancer:probes:detail',
                                    args=(lb_id, obj_id))

    DEPLOYED_STATUS_CHOICES = (
        ('true', True),
        ('false', False),
    )
    id = tables.Column('id', verbose_name=_('id'), hidden=True)
    name = tables.Column('name', verbose_name=_('Name'))
    type = tables.Column('type', verbose_name=_('Type'))
    deployed = tables.Column('deployed',
                             verbose_name=_('Deployed'),
                             status=True,
                             status_choices=DEPLOYED_STATUS_CHOICES)

    def __init__(self, *args, **kwargs):
        super(ProbesTable, self).__init__(*args, **kwargs)
        # NOTE(akscram): Set callable link to reverse URL with two
        #                arguments.
        self.columns['name'].link = self.link_callback

    class Meta:
        name = 'probes'
        verbose_name = _('Probes')
        status_columns = ['deployed']
        row_actions = (DeleteProbe,)
        table_actions = (CreateProbe, DeleteProbe)
