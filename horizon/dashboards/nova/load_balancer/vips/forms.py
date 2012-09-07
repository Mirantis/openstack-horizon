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

VIP_TYPE_CHOICES = (
    ('', '---------'),
    ('PRIVATE', 'Private'),
    ('PUBLIC', 'Public'),
)


class CreateVIP(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Virtual IP Name"))
    address = forms.IPAddressField(label=_('Virtual IP Address'))
    mask = forms.IPAddressField(label=_('Virtual IP Address Mask'))
    port = forms.IntegerField(min_value=1, max_value=65536,
                              label=_('Virtual IP Port'))
# NOTE(akscram): The Type of VIP not yet supported.
#    type = forms.ChoiceField(choices=VIP_TYPE_CHOICES, required=False,
#                             label=_('Virtual IP Type'))
    vlan = forms.IntegerField(min_value=1, max_value=4096,
                              required=False, label=_('Virtual IP VLAN'))

    def __init__(self, *args, **kwargs):
        self.lb_id = kwargs.pop('lb_id')
        super(CreateVIP, self).__init__(*args, **kwargs)

    def handle(self, request, data):
        try:
            api.vip_create(request, self.lb_id, data['name'],
                           data['address'], data['mask'], data['port'],
                           vlan=data['vlan'])
            msg = "Creating Virtual IP \"%s\"" % data['name']
            messages.success(request, msg)
        except balancerclient_exceptions.ClientException, e:
            exceptions.handle(request, _("Error to create Virtual IP: %r") %
                                       (e.message,))
        return shortcuts.redirect('horizon:nova:load_balancer:detail',
                                  lb_id=self.lb_id)
