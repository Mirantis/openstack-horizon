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

from django import shortcuts
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from horizon import forms
from horizon import api
from horizon import exceptions

from .vips.forms import VIP_TYPE_CHOICES

from balancerclient.common import exceptions as balancerclient_exceptions


LOG = logging.getLogger(__name__)

LB_ALGORITHMS = (
    ('ROUND_ROBIN', 'ROUND_ROBIN'),
    ('LEAST_CONNECTIONS', 'LEAST_CONNECTIONS'),
)

LB_PROTOCOLS = (
    ('HTTP', 'HTTP'),
)


class CreateLoadBalancer(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Load Balancer Name"))
    algorithm = forms.ChoiceField(choices=LB_ALGORITHMS,
                        label=_("Node selection algorithm of load balancing."))
    protocol = forms.ChoiceField(choices=LB_PROTOCOLS,
                                 label=_("Protocol of load balancing."))
    port = forms.IntegerField(min_value=1, max_value=65536, initial=80,
                              label=_("Port of load balancing."))
    vip_address = forms.IPAddressField(label=_('Virtual IP Address'))
    vip_mask = forms.IPAddressField(label=_('Virtual IP Address Mask'))
# NOTE(akcram): VIP type not yet supported in LBaaS.
#    vip_type = forms.ChoiceField(choices=VIP_TYPE_CHOICES, required=False,
#                                 label=_('Virtual IP Type'))
    vip_vlan = forms.IntegerField(required=False, label=_('Virtual IP VLAN'))

    def handle(self, request, data):
        try:
            # NOTE(akscram): The Port is a load balancing port and
            #                specified to LB and VIP.
            api.lb_create(request, data['name'], data['algorithm'],
                          data['protocol'], data['name'],
                          data['vip_address'], data['vip_mask'], data['port'],
                          vip_vlan=data['vip_vlan'], port=data['port'])
            message = "Creating load balancer \"%s\"" % data["name"]
            LOG.info(message)
            messages.info(request, message)
        except balancerclient_exceptions.ClientException, e:
            LOG.exception("ClientException in CreateLoadBalancer")
            messages.error(request,
                           _("Error Creating Load Balancer: %s") % e.message)
        return shortcuts.redirect("horizon:nova:load_balancer:index")


class UpdateLoadBalancer(forms.SelfHandlingForm):
    lb = forms.CharField(widget=forms.TextInput(
                                        attrs={'readonly': 'readonly'}),
                         label=_("Load Balancer"))
    name = forms.CharField(widget=forms.TextInput(
                                        attrs={'readonly': 'readonly'}))
    algorithm = forms.ChoiceField(choices=LB_ALGORITHMS,
                        label=_("Node selection algorithm of load balancing."))
    protocol = forms.CharField(required=True, initial='HTTP',
                               label=_("Protocol of load balancing"))
    port = forms.IntegerField(min_value=1, max_value=65536, initial=80,
                              label=_("Port of load balancing."))

    def handle(self, request, data):
        try:
            api.lb_update(request, data['lb'],
                          algorithm=data['algorithm'],
                          port=data['port'])
            messages.success(request,
                             _("Load Balancer \"%s\" updated.") % data['name'])
        except:
            exceptions.handle(request, _('Unable to update load balancer.'))
        return shortcuts.redirect('horizon:nova:load_balancer:index')
