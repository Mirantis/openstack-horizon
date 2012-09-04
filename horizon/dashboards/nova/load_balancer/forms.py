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


class CreateLoadBalancer(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Load Balancer Name"))
    algorithm = forms.ChoiceField(label=_("Node selection algorithm of load balancing."))
    protocol = forms.ChoiceField(label=_("Protocol of load balancing."))
    vip_address = forms.IPAddressField(required=False,
                                       label=_('Virtual IP Address'))
    vip_mask = forms.IPAddressField(required=False,
                                    label=_('Virtual IP Address Mask'))
    port = forms.IntegerField(min_value=1, max_value=65536, initial=80,
                              label=_("Virtual IP Port"))
# NOTE(akcram): VIP type not yet supported in LBaaS.
#    vip_type = forms.ChoiceField(choices=VIP_TYPE_CHOICES, required=False,
#                                 label=_('Virtual IP Type'))
    vip_vlan = forms.IntegerField(min_value=1, max_value=4096,
                                  required=False, label=_('Virtual IP VLAN'))

    def __init__(self, *args, **kwargs):
        algos = kwargs.pop('lb_algoritms', None)
        protos = kwargs.pop('lb_protocols', None)
        super(CreateLoadBalancer, self).__init__(*args, **kwargs)
        if not algos:
            protos = algos = (('', ''),)
        self.fields['algorithm'].choices = algos
        self.fields['protocol'].choices = protos

    def handle(self, request, data):
        try:
            lb = api.lb_create(request, data['name'], data['algorithm'],
                          data['protocol'])
            messages.success(request, ("Created load balancer \"%s\"" %
                                       data["name"]))
        except balancerclient_exceptions.ClientException, e:
            LOG.exception("ClientException in CreateLoadBalancer")
            messages.error(request,
                           _("Error Creating Load Balancer: %s") % e.message)
        else:
            if data['vip_address']:
                try:
                    # NOTE(akscram): Virtual IP created with empty name.
                    api.vip_create(request, lb.id, '', data['vip_address'],
                                   data['vip_mask'], data['port'],
                                   vlan=data['vip_vlan'])
                    messages.success(request, ("Created Virtual IP \"%s\"" %
                                               data["vip_address"]))
                except balancerclient_exceptions.ClientException, e:
                    LOG.exception("ClientException in CreateLoadBalancer")
                    messages.error(request,
                                   _("Error Creating Virtual IP: %s") % \
                                   e.message)
        return shortcuts.redirect("horizon:nova:load_balancer:index")


class UpdateLoadBalancer(forms.SelfHandlingForm):
    lb = forms.CharField(widget=forms.TextInput(
                                        attrs={'readonly': 'readonly'}),
                         label=_("Load Balancer"))
    name = forms.CharField(widget=forms.TextInput())
    algorithm = forms.ChoiceField(label=_("Node selection algorithm of load balancing."))
    protocol = forms.ChoiceField(label=_("Protocol of load balancing"))
    port = forms.IntegerField(min_value=1, max_value=65536, initial=80,
                              label=_("Port of load balancing."))

    def __init__(self, *args, **kwargs):
        algos = kwargs.pop('lb_algoritms')
        protos = kwargs.pop('lb_protocols')
        super(UpdateLoadBalancer, self).__init__(*args, **kwargs)
        self.fields['algorithm'].choices = algos
        self.fields['protocol'].choices = protos

    def handle(self, request, data):
        try:
            api.lb_update(request, data['lb'],
                          name=data['name'],
                          algorithm=data['algorithm'],
                          protocol=data['protocol'],
                          port=data['port'])
            messages.success(request,
                             _("Load Balancer \"%s\" updated.") % data['name'])
        except:
            exceptions.handle(request, _('Unable to update load balancer.'))
        return shortcuts.redirect('horizon:nova:load_balancer:index')
