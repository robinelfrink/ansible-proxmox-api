#!/usr/bin/python

# Copyright: (c) 2019 Robin Elfrink <robin@15augustus.nl>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: proxmox_api
short_description: Ansible module to interact with the Proxmox API
description:
    - Ansible module to interact with the Proxmox API
options:
    endpoint:
        description:
            - The endpoint to call.
        required: true
    method:
        description:
            - The HTTP method to use (GET/POST/...). Defaults to GET.
        required: false
    host:
        description:
            - The Proxmox host to communicate with.
        required: true
    port:
        description:
            - The port at which the Proxmox API listens. Defaults to 8006.
        required: false
    user:
        description:
            - The username to log in to Proxmox with.
        required: true
    password:
        description:
            - The user's password.
        required: true
    verify_ssl:
        description:
            - Verify the hosts SSL certificate. Defaults to True.
        required: false
    parameters:
        description:
            - Parameters to send in the body.
        required: false
author:
    - robin@15augustus.nl
'''

EXAMPLES = '''
- name: Get properties for all nodes
  proxmox_api:
    endpoint: /nodes
    host: proxmox.example.com
    user: admin
    password: secret
- name: Set a virtual machine to boot from hard disk
  proxmox_api:
    endpoint: '/nodes/{{ node }}/qemu/{{ vmid }}/config
    method: post
    host: proxmox.example.com
    user: admin
    password: secret
    parameters:
      boot: c
'''

from ansible.module_utils.basic import AnsibleModule
import json
import requests
from requests.exceptions import HTTPError
from requests.packages.urllib3.exceptions import InsecureRequestWarning

tickets = {}

def get_ticket(host, port, user, password, verify_ssl):
    if ('%s-%s-%s-%s' % (host, port, user, password)) in tickets:
        return tickets['%s-%s-%s' % (host, user, password)]
    response = requests.post(
        'https://%s:%d/api2/json/access/ticket' % (host, port),
        data = {
            'username': user,
            'password': password
        },
        verify = verify_ssl
    )
    if response.status_code!=200:
        response.raise_for_status()
    return response.json()['data']

def call_api(endpoint, method, host, port, user, password, verify_ssl, parameters):
    ticket = get_ticket(host, port, user, password, verify_ssl)
    response = requests.request(
        method.upper(),
        'https://%s:%d/api2/json/%s' % (host, port, endpoint),
        params = parameters if parameters and method.upper() in ['GET'] else None,
        data = parameters if parameters and method.upper() in ['POST', 'PUT'] else None,
        headers = {
            'Cookie': 'PVEAuthCookie=%s' % ticket['ticket'],
            'CSRFPreventionToken': ticket['CSRFPreventionToken'],
        },
        verify = verify_ssl
    )
    if response.status_code!=200:
        response.raise_for_status()
    return response.json()['data']

def main():
    module_args = dict(
        endpoint = dict(type='str', required=True),
        method = dict(type='str', required=False, default='GET'),
        host = dict(type='str', required=True),
        port = dict(type='int', required=False, default=8006),
        user = dict(type='str', required=True),
        password = dict(type='str', required=True, no_log=True),
        verify_ssl = dict(type='bool', required=False, default=True),
        parameters = dict(type='dict', required=False)
    )
    result = dict(
        changed = False
    )
    module = AnsibleModule(
        argument_spec = module_args,
        supports_check_mode = True
    )

    if not module.params.get('verify_ssl'):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    if module.check_mode:
        module.exit_json(**result)

    try:
        result['result'] = call_api(
            module.params.get('endpoint'),
            module.params.get('method'),
            module.params.get('host'),
            module.params.get('port'),
            module.params.get('user'),
            module.params.get('password'),
            module.params.get('verify_ssl'),
            module.params.get('parameters')
        )
        module.exit_json(**result)
    except HTTPError as e:
        result['msg'] = e.strerror
        result['body'] = e.response.request.body
        result['result'] = e.response.json()
        module.fail_json(**result)
    except Exception as e:
        result['msg'] = e.strerror
        module.fail_json(**result)

if __name__ == '__main__':
    main()
