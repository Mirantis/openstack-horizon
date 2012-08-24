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

from django.utils.translation import ugettext_lazy as _
from django.forms import widgets
from django.core.exceptions import ValidationError

from horizon import forms

from balancerclient.common import exceptions as balancerclient_exceptions


LOG = logging.getLogger(__name__)


def start_with_slash(s):
    if not s.startswith('/'):
        raise ValidationError(_('url must start with forward slash'))


class CreateProbe(forms.Form):
    TYPE_CHOICES = (
        ('ICMP', 'ICMP'),
        ('HTTP', 'HTTP'),
    )
    name = forms.CharField(max_length='255', label=_('Probe Name'))
    type = forms.ChoiceField(choices=TYPE_CHOICES, label=_('Proe Type'))
    interval = forms.IntegerField(label=_('Probe Interval'))


class CreateICMPProbe(forms.Form):
    delay = forms.IntegerField(label=_('Probe delay'))
    attempts = forms.IntegerField(label=_('Attempts before deactivation'))
    timeout = forms.IntegerField(label=_('Timeout'))


class CreateHTTPProbe(forms.Form):
    METHOD_CHOICES = (
        ('GET', 'GET'),
        ('HEAD', 'HEAD'),
    )
    path = forms.CharField(max_length=255, label=_('Probe HTTP URL'),
                           validators=[start_with_slash])
    method = forms.ChoiceField(choices=METHOD_CHOICES,
                               label=_('Probe HTTP Method'))
    status = forms.IntegerField(label=_('Expected HTTP Status'))
