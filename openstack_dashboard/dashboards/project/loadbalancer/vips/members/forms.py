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
import netaddr

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import forms
from horizon import messages
from horizon import exceptions
from horizon.utils import fields

from openstack_dashboard import api


LOG = logging.getLogger(__name__)

CONDITION_CHOICES = (
    ('ENABLED', 'ENABLED'),
    ('DISABLED', 'DISABLED'),
    )

NODE_NOVA_INSTANCE = 'NOVA_INSTANCE'


class CreateMember(forms.SelfHandlingForm):
    instance_id = forms.CharField(widget=forms.HiddenInput(
        attrs={'readonly': 'readonly'}))
    name = forms.CharField(max_length='255', label=_('Member Name'))
    address = forms.CharField()
    port = forms.IntegerField(min_value=1, max_value=65536, initial=80,
                              label=_('Service port.'))
    weight = forms.IntegerField(min_value=1, max_value=100000,
                                label=_('Member Weight'))
    condition = forms.ChoiceField(choices=CONDITION_CHOICES,
                                  label=_('Member Condition'))
    failure_url = 'horizon:project:loadbalancer:vip:detail'

#    def clean(self):
#        cleaned_data = super(CreateMember, self).clean()
#        gateway_ip = cleaned_data.get('gateway_ip')
#        return cleaned_data

    def handle(self, request, data):
        print "$$$$$"
        try:
            print data

            LOG.debug('params = %s' % data)
            member = api.quantum.subnet_create(request, **data)
            msg = _('Member %s was successfully created.') % data['name']
            LOG.debug(msg)
            messages.success(request, msg)
            return member
        except Exception:
            msg = _('Failed to create member %s') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url, args=[data['vip_id']])
            exceptions.handle(request, msg, redirect=redirect)

    def is_valid(self):
        return True


class UpdateMember(forms.SelfHandlingForm):
    network_id = forms.CharField(widget=forms.HiddenInput())
    subnet_id = forms.CharField(widget=forms.HiddenInput())
    cidr = forms.CharField(widget=forms.HiddenInput())
    ip_version = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(max_length=255,
                           label=_("Name"),
                           required=False)
    gateway_ip = fields.IPField(label=_("Gateway IP"),
                                required=True,
                                initial="",
                                help_text=_("IP address of Gateway "
                                            "(e.g. 192.168.0.1)"),
                                version=fields.IPv4 | fields.IPv6,
                                mask=False)
    failure_url = 'horizon:project:networks:detail'

    def clean(self):
        cleaned_data = super(UpdateMember, self).clean()
        ip_version = int(cleaned_data.get('ip_version'))
        gateway_ip = cleaned_data.get('gateway_ip')
        if gateway_ip:
            if netaddr.IPAddress(gateway_ip).version is not ip_version:
                msg = _('Gateway IP and IP version are inconsistent.')
                raise forms.ValidationError(msg)
        return cleaned_data

    def handle(self, request, data):
        try:
            LOG.debug('params = %s' % data)
            params = {'name': data['name']}
            params['gateway_ip'] = data['gateway_ip']
            subnet = api.quantum.subnet_modify(request, data['subnet_id'],
                                               name=data['name'],
                                               gateway_ip=data['gateway_ip'])
            msg = _('Subnet %s was successfully updated.') % data['cidr']
            LOG.debug(msg)
            messages.success(request, msg)
            return subnet
        except Exception:
            msg = _('Failed to update subnet %s') % data['cidr']
            LOG.info(msg)
            redirect = reverse(self.failure_url, args=[data['network_id']])
            exceptions.handle(request, msg, redirect=redirect)
