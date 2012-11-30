from __future__ import absolute_import

import logging

from quantumclient.v2_0 import client as quantum_client
from django.utils.datastructures import SortedDict

from openstack_dashboard.api.base import APIDictWrapper, url_for


LOG = logging.getLogger(__name__)

def quantumclient(request):
    LOG.debug('quantumclient connection created using token "%s" and url "%s"'
              % (request.user.token.id, url_for(request, 'network')))
    LOG.debug('user_id=%(user)s, tenant_id=%(tenant)s' %
              {'user': request.user.id, 'tenant': request.user.tenant_id})
    c = quantum_client.Client(token=request.user.token.id,
                              endpoint_url=url_for(request, 'network'))
    return c

class QuantumAPIDictWrapper(APIDictWrapper):

    def set_id_as_name_if_empty(self, length=8):
        try:
            if not self._apidict['name']:
                id = self._apidict['id']
                if length:
                    id = id[:length]
                self._apidict['name'] = '(%s)' % id
        except KeyError:
            pass

    def items(self):
        return self._apidict.items()


class Service(QuantumAPIDictWrapper):
    """Wrapper for quantum Networks"""
    _attrs = ['name', 'id', 'tenant_id']

def service_list(request, **params):
    LOG.debug("service_list(): params=%s" % (params))
#    services = quantumclient(request).list_networks(**params).get('services')
    services = [{'id': '1234567890', 'name': 'lbaas', 'tenant_id': '123'}]
    return [Service(n) for n in services]

def service_get(request, service_id, **params):
    return Service({'id': '1234567890', 'name': 'lbaas', 'tenant_id': '123'})

class Vip(QuantumAPIDictWrapper):
    _attrs = ['name', 'id', 'tenant_id', 'address']

def vip_list(request, **params):
    vips = [{'id': 'agsfas', 'name': 'vip #1', 'tenant_id': '123', 'address': '127.0.0.1'},
            {'id': 'agsfaa', 'name': 'vip #2', 'tenant_id': '123', 'address': '127.0.0.2'}]
    return [Vip(n) for n in vips]
