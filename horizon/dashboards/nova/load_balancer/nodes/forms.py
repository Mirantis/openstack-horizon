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

from balancerclient.common import exceptions as balancerclient_exceptions


LOG = logging.getLogger(__name__)


CONDITION_CHOICES = (
    ('ENABLED', 'ENABLED'),
    ('DISABLED', 'DISABLED'),
)


class CreateForm(forms.SelfHandlingForm):
    lb_id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(max_length='255', label=_('Node Name'))
    address = forms.IPAddressField(label=_('Node Address'))
    port = forms.IntegerField(min_value=1, max_value=65536, initial=80,
                              label=_('Port of load balancing.'))
    weight = forms.IntegerField(label=_('Node Weight'))
    condition = forms.ChoiceField(choices=CONDITION_CHOICES,
                                  label=_('Node Condition'))

    def handle(self, request, data):
        try:
            # FIXME(akscram): type and status are hardcoded.
            api.node_create(request, data['lb_id'], data['name'], 'HW',
                            data['address'], data['port'], data['weight'], '',
                            condition=data['condition'])
            message = "Creating node \"%s\"" % data['name']
            LOG.info(message)
            messages.info(request, message)
        except balancerclient_exceptions.ClientException, e:
            LOG.exception('ClientException in CreateNode')
            messages.error(request,
                           _("Error Creating node: %s") % e.message)
        return shortcuts.redirect('horizon:nova:load_balancer:detail',
                                  lb_id=data['lb_id'])


class UpdateForm(forms.SelfHandlingForm):
    lb_id = forms.CharField(widget=forms.HiddenInput())
    node_id = forms.CharField(widget=forms.TextInput(
                                            attrs={'readonly': 'readonly'}))
    name = forms.CharField(max_length='255', label=_('Node Name'))
    address = forms.IPAddressField(label=_('Node Address'))
    port = forms.IntegerField(min_value=1, max_value=65536, initial=80,
                              label=_('Port of load balancing.'))
    weight = forms.IntegerField(label=_('Node Weight'))
    condition = forms.ChoiceField(choices=CONDITION_CHOICES,
                                  label=_('Node Condition'))

    def handle(self, request, data):
        try:
            api.node_update(request, data['lb_id'], data['node_id'],
                            name=data['name'],
                            address=data['address'],
                            port=data['port'],
                            weight=data['weight'],
                            condition=data['condition'])
            messages.success(request,
                             _("Node \"%s\" updated.") % data['name'])
        except:
            exceptions.handle(request, _('Unable to update node balancer.'))
        return shortcuts.redirect('horizon:nova:load_balancer:detail',
                                  lb_id=data['lb_id'])
