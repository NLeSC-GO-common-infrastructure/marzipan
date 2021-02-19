# Marzipan ansible playbooks

The `ansible_playbooks` folder in this subdirectory contains several ansible playbooks specifying further setup actions performed across all created VMs/nodes. Ansible provides a tool to script such provisioning actions for execution across distributed systems.

Of particular importance are the `firewall.yml`, `set_ssh_keys.yml`, and `update_hosts_file.yml`. However, no modifications are required.
The first defines firewall settings, the second copys ssh keys to all VMs enabling access, and the last creates/upates a file with all cluster hosts.
The hosts file is/can be used by subsequent ansible playbooks (e.g. those in `emma_marzipan`) to provision all VMs/nodes with desired software, as well as to start and stop cluster sevices such as, e.g. Dask.