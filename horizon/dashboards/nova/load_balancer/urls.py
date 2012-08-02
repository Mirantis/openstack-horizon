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

from django.conf.urls.defaults import *

from .views import (IndexView, CreateView, UpdateView, DetailView,
                    LoadBalancingView)
from .nodes import urls as nodes_urls
from .probes import urls as probes_urls

import logging
LOG = logging.getLogger(__name__)

def test(request, *args, **kwargs):
    LOG.debug("Request: %r" % request)
    raise Exception


lbs_urlpatterns = patterns('horizon.dashboards.nova.load_balancer.views',
    url(r'^$', DetailView.as_view(), name='detail'),
    url(r'^update$', UpdateView.as_view(), name='update'),
    url(r'^nodes/', include(nodes_urls, namespace='nodes')),
    url(r'^probes/', include(probes_urls, namespace='probes')),
)

urlpatterns = patterns('horizon.dashboards.nova.load_balancer.views',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^create/$', CreateView.as_view(), name='create'),
    url(r'^loadbalancing/$', LoadBalancingView.as_view(), name='loadbalancing'),
    url(r'^(?P<lb_id>[^/]+)/', include(lbs_urlpatterns)),
)
