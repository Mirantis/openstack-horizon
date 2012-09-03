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
from django.forms import formsets
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

NODE_NOVA_INSTANCE = 'NOVA_INSTANCE'


class BaseNodeFormSet(formsets.BaseFormSet):
    def get_node_address_choices(self, instance):
        choices = []
        for label, addresses in instance.addresses.items():
            for address in addresses:
                item_label = "%s [%s]" % (address['addr'], label)
                choices.append((address['addr'], item_label))
        return choices

    def add_fields(self, form, index):
        super(BaseNodeFormSet, self).add_fields(form, index)
        instance = self.initial[index]['instance']
        choices = self.get_node_address_choices(instance)
        form.fields['address'] = forms.ChoiceField(label=_('Node Address'),
                                    choices=self.get_node_address_choices(instance))


class AddNode(forms.SelfHandlingForm):
    instance_id = forms.CharField(widget=forms.HiddenInput(
                                             attrs={'readonly': 'readonly'}))
    name = forms.CharField(max_length='255', label=_('Node Name'))
    address = forms.ChoiceField(label=_('Node Address'))
    lb = forms.ChoiceField(label=_('Load Balancer'))
    port = forms.IntegerField(min_value=1, max_value=65536, initial=80,
                              label=_('Port of load balancing.'))
    weight = forms.IntegerField(label=_('Node Weight'))
    condition = forms.ChoiceField(choices=CONDITION_CHOICES,
                                  label=_('Node Condition'))

    def __init__(self, *args, **kwargs):
        lb_choices = kwargs.pop('lb_choices')
        address_choices = kwargs.pop('address_choices')
        super(AddNode, self).__init__(*args, **kwargs)
        self.fields['lb'].choices = lb_choices
        self.fields['address'].choices = address_choices

    def handle(self, request, data):
        try:
            # NOTE(akscram): hardcoded NOVA_INSTANCE for horizon.
            api.node_create(request, data['lb'], data['name'],
                            NODE_NOVA_INSTANCE,
                            data['address'], data['port'], data['weight'],
                            data['condition'],
                            instance_id=data['instance_id'])
            msg = "Creating node \"%s\"" % data['name']
            messages.success(request, msg)
        except balancerclient_exceptions.ClientException, e:
            exceptions.handle(request,
                              _("Error to create node: %r") % (e.message,))
        return shortcuts.redirect('horizon:nova:instances_and_volumes:index')


class CreateNode(forms.Form):
    instance_id = forms.CharField(widget=forms.HiddenInput(
                                               attrs={'readonly': 'readonly'}))
    name = forms.CharField(max_length='255', label=_('Node Name'))
    # NOTE(akscram): the field 'address' replaced in formset.
    address = forms.CharField()
    port = forms.IntegerField(min_value=1, max_value=65536, initial=80,
                              label=_('Port of load balancing.'))
    weight = forms.IntegerField(min_value=1, max_value=100000,
                                label=_('Node Weight'))
    condition = forms.ChoiceField(choices=CONDITION_CHOICES,
                                  label=_('Node Condition'))


class UpdateNode(forms.SelfHandlingForm):
    lb_id = forms.CharField(widget=forms.HiddenInput())
    node_id = forms.CharField(widget=forms.TextInput(
                                            attrs={'readonly': 'readonly'}))
    name = forms.CharField(max_length='255', label=_('Node Name'))
    address = forms.ChoiceField(label=_('Node Address'))
    port = forms.IntegerField(min_value=1, max_value=65536, initial=80,
                              label=_('Port of load balancing.'))
    weight = forms.IntegerField(min_value=1, max_value=100000,
                                label=_('Node Weight'))
    condition = forms.ChoiceField(choices=CONDITION_CHOICES,
                                  label=_('Node Condition'))

    def __init__(self, *args, **kwargs):
        address_choices = kwargs.pop('address_choices')
        super(UpdateNode, self).__init__(*args, **kwargs)
        self.fields['address'].choices = address_choices

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
