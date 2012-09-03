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

from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import tables


LOG = logging.getLogger(__name__)


class SubLBLinkAction(tables.LinkAction):
    def get_link_args(self, datum=None):
        lb_id = self.table.kwargs['lb_id']
        args = super(SubLBLinkAction, self).get_link_args(datum)
        return (lb_id,) + args


class DeleteLoadBalancer(tables.DeleteAction):
    data_type_singular = _("Load Balancer")
    data_type_plural = _("Load Balancers")

    def delete(self, request, lb_id):
        api.lb_delete(request, lb_id)


class CreateLoadBalancer(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Load Balancer")
    url = "horizon:nova:load_balancer:create"
    classes = ("ajax-modal", "btn-create")


class EditLoadBalancer(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit Load Balancer")
    url = "horizon:nova:load_balancer:update"
    classes = ("ajax-modal", "btn-edit")


class LoadBalancersTable(tables.DataTable):
    STATUS_CHOICES = (
        ("active", True),
        ('build', None),
        ('', None),
        ('error', False),
    )
    id = tables.Column("id", verbose_name=_('id'), hidden=True)
    name = tables.Column("name", verbose_name=_('Name'),
                         link='horizon:nova:load_balancer:detail')
    algorithm = tables.Column("algorithm", verbose_name=_("Algorithm"))
    status = tables.Column("status",
                           verbose_name=_("Status"),
                           status=True,
                           status_choices=STATUS_CHOICES)

    class Meta:
        name = "loadbalancers"
        verbose_name = _("Load Balancers")
        status_columns = ["status"]
        row_actions = (EditLoadBalancer, DeleteLoadBalancer)
        table_actions = (CreateLoadBalancer, DeleteLoadBalancer)


class LBTable(tables.DataTable):
    STATUS_CHOICES = (
        ("active", True),
        ('build', None),
        ('', None),
        ('error', False),
    )
    id = tables.Column("id", verbose_name=_('id'), hidden=True)
    name = tables.Column("name", verbose_name=_('Name'))
    algorithm = tables.Column("algorithm", verbose_name=_("Algorithm"))
    protocol = tables.Column("protocol", verbose_name=_("Protocol"))
    status = tables.Column("status",
                           verbose_name=_("Status"),
                           status=True,
                           status_choices=STATUS_CHOICES)

    class Meta:
        name = "lb"
        verbose_name = _("Load Balancer")
