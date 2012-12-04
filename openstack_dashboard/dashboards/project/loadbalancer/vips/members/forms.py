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


class CreateMember(forms.Form):
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

