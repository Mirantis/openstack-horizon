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

from django.core import urlresolvers

from horizon import api
from horizon import forms
from horizon import tabs
from horizon import exceptions

from .forms import CreateVIP
from .tabs import VIPDetailTabs


LOG = logging.getLogger(__name__)


class CreateView(forms.ModalFormView):
    form_class = CreateVIP
    template_name = 'nova/load_balancer/vips/create.html'

    def get_form_kwargs(self):
        kwargs = super(CreateView, self).get_form_kwargs()
        kwargs['lb_id'] = self.kwargs['lb_id']
        return kwargs

    def get_initial(self):
        return {'port': 80,
                'mask': '255.255.255.255'}


class DetailView(tabs.TabView):
    tab_group_class = VIPDetailTabs
    template_name = 'nova/load_balancer/vips/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["vip"] = self.get_data()
        return context

    def get_data(self):
        if not hasattr(self, "_vip"):
            lb_id = self.kwargs['lb_id']
            vip_id = self.kwargs['vip_id']
            try:
                vip = api.vip_get(self.request, lb_id, vip_id)
            except:
                redirect = urlresolvers.reverse(
                                   'horizon:nova:load_balancer:detail',
                                   args=(lb_id,))
                exceptions.handle(self.request,
                                  _('Unable to retrieve details for '
                                    'Virtual IP "%s".') % (vip_id,),
                                    redirect=redirect)
            self._vip = vip
        return self._vip

    def get_tabs(self, request, *args, **kwargs):
        vip = self.get_data()
        return self.tab_group_class(request, vip=vip, **kwargs)
