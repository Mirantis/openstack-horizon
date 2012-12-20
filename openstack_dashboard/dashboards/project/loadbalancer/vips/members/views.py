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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import forms, exceptions
from openstack_dashboard import api
from .forms import CreateMember
from .forms import UpdateMember


class CreateView(forms.ModalFormView):
    form_class = CreateMember
    template_name = 'project/loadbalancer/vips/members/create.html'
#    success_url = 'horizon:project:loadbalancer:vips:members:create_member'

#    def get_success_url(self):
#        print "$$$"
#        return reverse(self.success_url, args=(self.kwargs['vip_id'],))

    def get_object(self):
        if not hasattr(self, "_object"):
            try:
                vip_id = self.kwargs["vip_id"]
                self._object = api.quantum_lb.vip_get(self.request, vip_id)
            except:
                redirect = reverse('horizon:project:loadbalancer:index')
                msg = _("Unable to retrieve vip.")
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['vip'] = self.get_object()
        return context

#    def get_initial(self):
#        vip = self.get_object()
#        return {"vip_id": self.kwargs['vip_id'],
#                "vip_name": vip.name}


class UpdateView(forms.ModalFormView):
    form_class = UpdateMember
    template_name = 'project/networks/subnets/update.html'
    context_object_name = 'subnet'
    success_url = 'horizon:project:loadbalancer:vips:members:create_member'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['vip_id', 'member_id'],))

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            member_id = self.kwargs['member_id']
            try:
                self._object = api.quantum_lb.member_get(self.request, member_id)
            except:
                redirect = reverse("horizon:project:networks:index")
                msg = _('Unable to retrieve subnet details')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        member = self._get_object()
        context['member_id'] = member.id
        context['vip_id'] = member.vip_id
        return context

    def get_initial(self):
        member = self._get_object()
        return {'vip_id': self.kwargs['vip_id'],
                'member_id': member['id'],
                'name': member['name'],
                }
