# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Nebula, Inc.
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

from django import template
from django.template.defaultfilters import title
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import tables
from horizon.templatetags import sizeformat


LOG = logging.getLogger(__name__)

ACTIVE_STATES = ("ACTIVE",)

POWER_STATES = {
    0: "NO STATE",
    1: "RUNNING",
    2: "BLOCKED",
    3: "PAUSED",
    4: "SHUTDOWN",
    5: "SHUTOFF",
    6: "CRASHED",
    7: "SUSPENDED",
    8: "FAILED",
    9: "BUILDING",
}

PAUSE = 0
UNPAUSE = 1
SUSPEND = 0
RESUME = 1

class AddProbe(tables.LinkAction):
    name = "addprobe"
    verbose_name = _("Manage Probe")
    url = "horizon:nova:load_balancer:devices:addprobe"
    classes = ("ajax-modal", "btn-camera")

    def allowed(self, request, balancer=None):
        return balancer.status in ACTIVE_STATES

class AddSticky(tables.LinkAction):
    name = "addsticky"
    verbose_name = _("Manage Sticky")
    url = "horizon:nova:load_balancer:devices:addsticky"
    classes = ("ajax-modal", "btn-camera")

    def allowed(self, request, balancer=None):
        return balancer.status in ACTIVE_STATES

class AddDevice(tables.LinkAction):
    name = "add_device"
    verbose_name = _("Create Load Balance")
    classes = ("ajax-modal","btn-edit",)
    url = "horizon:nova:load_balancer:devices:add_device"


class DeleteDevice(tables.BatchAction):
    name = "delete_device"
    action_present = _("Delete")
    action_past = _("Deleted")
    data_type_singular = _("Load Balance")
    data_type_plural = _("Load Balance")
    classes = ('btn-danger',)

    def action(self, request, lb_id):
        api.balancer_delete_lb(request, lb_id)


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, lb_id):
        LOG.debug ("Retrieve loadbalancer instance")
        instance = api.balancer_get_loadbalancer(request, lb_id)
        nodes = api.balancer_get_nodes_of_lb(request,  lb_id)
        str = ""
        for node in nodes:
                str = str + node.vm_instance+ "(" + node.address+":" + node.port+")["+self.statusMark(node['state'])+"] "
        instance.set('nodes',  str) 
        return instance
        
    def statusMark(self,  status):
        if status == "inservice":
            return 'A'
        else:
            return 'D'


def replace_underscores(string):
    return string.replace("_", " ")


class LBTable(tables.DataTable):
    STATUS_CHOICES = (
        ("active", True),
        ('build',  None), 
        ('error',  False), 
        
    )
    id = tables.Column("id", verbose_name=_('id'), hidden=True)
    name = tables.Column("name", verbose_name=_('Name'))
    alg = tables.Column("algorithm", verbose_name=_("Algorithm"))
    nodes = tables.Column("nodes",  verbose_name=_("Nodes"))
    status = tables.Column("status",
                           verbose_name=_("Status"),
                           status=True, 
                           status_choices=STATUS_CHOICES
                           )

    class Meta:
        name = "balancers"
        verbose_name = _("Balancers")
        status_columns = ["status"]
        row_class = UpdateRow
        table_actions = (AddDevice, DeleteDevice)
        row_actions = (AddProbe,  AddSticky)
