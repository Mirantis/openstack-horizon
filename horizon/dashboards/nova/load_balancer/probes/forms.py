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


class CreateForm(forms.SelfHandlingForm):
    TYPE_CHOICES = (
        ('ICMP', 'ICMP'),
        ('HTTP', 'HTTP'),
    )
    lb_id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(max_length='255', label=_('Node Name'))
    type = forms.ChoiceField(choices=TYPE_CHOICES, label=_('Probe Type'))
    # FIXME(akscram): not specified attributes for different types.

    def handle(self, request, data):
        try:
            api.probe_create(request, data['lb_id'], data['name'],
                             data['type'])
            message = "Creating probe \"%s\"" % data['name']
            LOG.info(message)
            messages.info(request, message)
        except balancerclient_exceptions.ClientException, e:
            LOG.exception('ClientException in CreateProbe')
            messages.error(request,
                           _("Error Creating probe: %s") % e.message)
        return shortcuts.redirect('horizon:nova:load_balancer:detail',
                                  lb_id=data['lb_id'])
