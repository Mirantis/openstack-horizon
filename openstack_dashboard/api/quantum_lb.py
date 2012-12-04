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

class Vip(QuantumAPIDictWrapper):
    _attrs = ['name', 'id', 'tenant_id', 'address', 'port']

def vip_list(request, **params):
    vips = []
    for i in range(10):
        vips.append({'id': 'agsfas%s' % i, 'name': 'vip #%s' % i, 'tenant_id': '123', 'address': '127.0.0.%s' % i, 'port': '100%s' % i})
    return [Vip(n) for n in vips]


class Member(QuantumAPIDictWrapper):
    _attrs = ['name', 'id', 'tenant_id', 'address', 'port']

def member_list(request, **params):
    members = []
    for i in range(15):
        members.append({'id': 'agsfas%s' % i, 'name': 'member #%s' % i, 'tenant_id': '123', 'address': '10.1.2.%s' % i, 'port': '30%s' % i})
    return [Vip(n) for n in members]
