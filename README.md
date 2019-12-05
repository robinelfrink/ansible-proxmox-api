# Ansible Proxmox API

`proxmox_api` is an Ansible module to interact with
[the Proxmox API](https://pve.proxmox.com/pve-docs/api-viewer/).

## Parameters

| Parameter  | Type   | Default | Description                                |
| ---------- | ------ | ------- | ------------------------------------------ |
| endpoint   | `str`  |         | The endpoint to call.                      |
| method     | `str`  | `GET `  | The HTTP method to use (GET/POST/...).     |
| host       | `str`  |         | The Proxmox host to communicate with.      |
| port       | `int`  | `8006`  | The port at which the Proxmox API listens. |
| user       | `str`  |         | The username to log in to Proxmox with.    |
| password   | `str`  |         | The user's password.                       |
| verify_ssl | `bool` | `True`  | Verify the hosts SSL certificate.          |
| parameters | `dict` |         | Parameters to send in the body.            |

## Examples

### Get properties for all nodes

```yaml
- name: Get properties for all nodes
  proxmox_api:
    endpoint: /nodes
    host: proxmox.example.com
    user: admin
    password: secret
```

### Set a virtual machine to boot from hard disk

```yaml
- name: Set a virtual machine to boot from hard disk
  proxmox_api:
    endpoint: '/nodes/{{ node }}/qemu/{{ vmid }}/config
    method: post
    host: proxmox.example.com
    user: admin
    password: secret
    parameters:
      boot: c
```
