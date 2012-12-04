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

from django.conf.urls.defaults import patterns, url, include

from .views import IndexView
#from .subnets.views import CreateView as AddSubnetView
#from .subnets.views import UpdateView as EditSubnetView
from .vips import urls as vip_urls
#from .ports import urls as port_urls


LOADBALANCERS = r'^(?P<service_id>[^/]+)/%s$'


urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
#    url(r'^create$', CreateView.as_view(), name='create'),
#    url(LOADBALANCERS % 'detail', DetailView.as_view(), name='detail'),
#    url(SERVICES % 'update', UpdateView.as_view(), name='update'),
#    url(SERVICES % 'subnets/create', AddSubnetView.as_view(),
#        name='addsubnet'),
#    url(r'^(?P<network_id>[^/]+)/subnets/(?P<subnet_id>[^/]+)/update$',
#        EditSubnetView.as_view(), name='editsubnet'),
    url(r'^vips/', include(vip_urls, namespace='subnets')),
#    url(r'^ports/', include(port_urls, namespace='ports'))
    )
