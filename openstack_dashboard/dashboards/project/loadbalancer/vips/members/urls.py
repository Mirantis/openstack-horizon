# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 NEC Corporation
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

from django.conf.urls import patterns, url
from openstack_dashboard.dashboards.project.loadbalancer.vips.members.views \
import CreateView

#from .views import DetailView
from .views import CreateView as AddMemberView

MEMBERS = r'^(?P<member_id>[^/]+)/%s$'
VIEW_MOD = 'openstack_dashboard.dashboards.project.loadbalancer.vips.members.views'


urlpatterns = patterns(VIEW_MOD,
#    url(MEMBERS % 'detail', DetailView.as_view(), name='detail'),
    url(r'^create', AddMemberView.as_view(), name='create'),
    url(MEMBERS % 'update', AddMemberView.as_view(), name='update'),
)
