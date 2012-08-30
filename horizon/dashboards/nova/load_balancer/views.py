# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
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

"""
Views for Instances and Volumes.
"""
import logging

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict
from novaclient import exceptions as novaclient_exceptions

from horizon import api
from horizon import exceptions
from horizon import tables
from horizon import forms
from .devices.tables import LBTable

LOG = logging.getLogger(__name__)

class IndexView(tables.MultiTableView):
    table_classes = (LBTable,)
    template_name = 'nova/load_balancer/index.html'

    def get_balancers_data(self):
        try:
            LOG.debug("Retrieve loadbalancers list %s" % self.request)
            devices = api.balancer_get_loadbalancers(self.request)
            for dev in devices:
                nodes = api.balancer_get_nodes_of_lb(self.request, dev.id)
                str = ""
                for node in nodes:
                    str = str + node.vm_instance+ "(" + node.address+":" + node.port+")["+self.statusMark(node['state'])+"] "
                dev.set('nodes',  str) 
            LOG.debug("Got the list: %s"%devices)
        except:
            devices = []
            exceptions.handle(self.request, _('Unable to retrieve devices.'))
        return devices
        
    def statusMark(self,  status):
        if status == "inservice":
            return 'A'
        else:
            return 'D'

