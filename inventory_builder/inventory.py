#!/usr/bin/env python3
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Usage: inventory.py ip1 [ip2 ...]
# Examples: inventory.py 10.10.1.3 10.10.1.4 10.10.1.5
#
# Advanced usage:
# Add another host after initial creation: inventory.py 10.10.1.5
# Add range of hosts: inventory.py 10.10.1.3-10.10.1.5
# Add hosts with different ip and access ip:
# inventory.py 10.0.0.1,192.168.10.1 10.0.0.2,192.168.10.2 10.0.0.3,192.168.1.3
# Delete a host: inventory.py -10.10.1.3
# Delete a host by id: inventory.py -node1
#
# Load a YAML or JSON file with inventory data: inventory.py load hosts.yaml
# YAML file should be in the following format:
#    group1:
#      host1:
#        ip: X.X.X.X
#        var: val
#    group2:
#      host2:
#        ip: X.X.X.X

from collections import OrderedDict
from ipaddress import ip_address
from ruamel.yaml import YAML

import os
import re
import sys

ROLES = ['all', 'docker-swarm-manager', 'docker-swarm-worker', 'docker',
'glusterfs-primary', 'glusterfs-second', 'glusterfs',
'minio-server', 'minio-worker', 'minio',
'hadoop-namenode', 'hadoop-resourcemanager', 'hadoop-datanode', 'hadoop',
'spark-master', 'spark-worker', 'spark',
'cassandra-seeds', 'cassandra-nodes', 'cassandra',
'jupyterhub',
'dask-scheduler', 'dask-worker', 'dask']

PROTECTED_NAMES = ROLES

AVAILABLE_COMMANDS = ['help', 'print_cfg', 'print_ips', 'load']
_boolean_states = {'1': True, 'yes': True, 'true': True, 'on': True,
                   '0': False, 'no': False, 'false': False, 'off': False}

yaml = YAML()
yaml.preserve_quotes = True
yaml.Representer.add_representer(OrderedDict, yaml.Representer.represent_dict)


def get_var_as_bool(name, default):
    value = os.environ.get(name, '')
    return _boolean_states.get(value.lower(), default)

# Configurable as shell vars start

#CONFIG_FILE = os.environ.get("CONFIG_FILE", "./hosts.yaml")
# Reconfigures cluster distribution at scale
#DEBUG = get_var_as_bool("DEBUG", True)
#HOST_PREFIX = os.environ.get("HOST_PREFIX", "node")

#HEKETI_ADMIN_KEY = os.environ.get("HEKETI_ADMIN_KEY", 'esciencerocks')
#HEKETI_USER_KEY = os.environ.get("HEKETI_USER_KEY", 'esciencerocks')


#CASSANDRA_SEEDS_COUNT = os.environ.get("CASSANDRA_SEEDS_COUNT", 2)

# Configurable as shell vars end
"""
Reimplementation of shell vars with their default values. These
be set by explicit calls prior to use of any methods/class methods
"""
DEBUG = True
HOST_PREFIX = "node"
CASSANDRA_SEEDS_COUNT = 2


class MarzipanInventory(object):

    def __init__(self, changed_hosts=None, config_file=None):
        self.config_file = config_file
        self.yaml_config = {}
        if self.config_file:
            try:
                self.hosts_file = open(config_file, 'r')
                self.yaml_config = yaml.load(self.hosts_file)
            except FileNotFoundError:
                pass

        if changed_hosts and changed_hosts[0] in AVAILABLE_COMMANDS:
            self.parse_command(changed_hosts[0], changed_hosts[1:])
            sys.exit(0)

        self.ensure_required_groups(ROLES)

        if changed_hosts:
            changed_hosts = self.range2ips(changed_hosts)
            print('changed hosts : ',changed_hosts)
            self.hosts = self.build_hostnames(changed_hosts)
            print('hosts : ',self.hosts)
            self.purge_invalid_hosts(self.hosts.keys(), PROTECTED_NAMES)

            # all_vars = {'heketi_admin_key': HEKETI_ADMIN_KEY, 'heketi_user_key': HEKETI_USER_KEY}
            all_vars = {}

            self.set_all(hosts = self.hosts, vars = all_vars)

            self.set_docker(list(self.hosts.keys()))
            self.set_glusterfs(list(self.hosts.keys()))
            self.set_minio(list(self.hosts.keys()))
            self.set_hadoop(list(self.hosts.keys()))
            self.set_spark(list(self.hosts.keys()))
            self.set_cassandra(list(self.hosts.keys()))
            self.set_jupyterhub(list(self.hosts.keys()))
            self.set_dask(list(self.hosts.keys()))

            # heketi_vars = {'disk_volume_device_1': "/dev/vdb"}
            # self.set_heketi(hosts = self.hosts, vars = heketi_vars)

        else:  # Show help if no options
            self.show_help()
            sys.exit(0)

        self.write_config(self.config_file)

    def write_config(self, config_file):
        if config_file:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.yaml_config, f)

        else:
            print("WARNING: Unable to save config. Make sure you set "
                  "CONFIG_FILE env var.")

    def debug(self, msg):
        if DEBUG:
            print("DEBUG: {0}".format(msg))

    def get_ip_from_opts(self, optstring):
        if 'ip' in optstring:
            return optstring['ip']
        else:
            raise ValueError("IP parameter not found in options")

    def ensure_required_groups(self, groups):
        for group in groups:
            if group == 'all':
                self.debug("Adding group {0}".format(group))
                if group not in self.yaml_config:
                    all_dict = OrderedDict([('vars', OrderedDict({})),
                                            ('hosts', OrderedDict({})),
                                            ('children', OrderedDict({}))])
                    self.yaml_config = {'all': all_dict}
            else:
                self.debug("Adding group {0}".format(group))
                if group not in self.yaml_config['all']['children']:
                    self.yaml_config['all']['children'][group] = {'vars': {}, 'hosts': {}}

    def get_host_id(self, host):
        '''Returns integer host ID (without padding) from a given hostname.'''
        try:
            short_hostname = host.split('.')[0]
            return int(re.findall("\\d+$", short_hostname)[-1])
        except IndexError:
            raise ValueError("Host name must end in an integer")

    def build_hostnames(self, changed_hosts):
        existing_hosts = OrderedDict()
        highest_host_id = -1
        print('highest_host_id',highest_host_id)
        try:
            for host in self.yaml_config['all']['hosts']:
                existing_hosts[host] = self.yaml_config['all']['hosts'][host]
                host_id = self.get_host_id(host)
                if host_id > highest_host_id:
                    highest_host_id = host_id
        except Exception:
            pass

        # FIXME(mattymo): Fix condition where delete then add reuses highest id
        print('highest_host_id',highest_host_id)
        next_host_id = highest_host_id + 1

        all_hosts = existing_hosts.copy()
        for host in changed_hosts:
            if host[0] == "-":
                realhost = host[1:]
                if self.exists_hostname(all_hosts, realhost):
                    self.debug("Marked {0} for deletion.".format(realhost))
                    all_hosts.pop(realhost)
                elif self.exists_ip(all_hosts, realhost):
                    self.debug("Marked {0} for deletion.".format(realhost))
                    self.delete_host_by_ip(all_hosts, realhost)
            elif host[0].isdigit():
                if ',' in host:
                    ip, access_ip = host.split(',')
                else:
                    ip = host
                    access_ip = host
                if self.exists_hostname(all_hosts, host):
                    self.debug("Skipping existing host {0}.".format(host))
                    continue
                elif self.exists_ip(all_hosts, ip):
                    self.debug("Skipping existing host {0}.".format(ip))
                    continue

                next_host = "{0}{1}".format(HOST_PREFIX, next_host_id)
                print('next_host',next_host)
                next_host_id += 1
                all_hosts[next_host] = {'ansible_host': access_ip,
                                        'ip': ip,
                                        'access_ip': access_ip}
            elif host[0].isalpha():
                raise Exception("Adding hosts by hostname is not supported.")

        return all_hosts

    def range2ips(self, hosts):
        reworked_hosts = []

        def ips(start_address, end_address):
            try:
                # Python 3.x
                start = int(ip_address(start_address))
                end   = int(ip_address(end_address))
            except:
                # Python 2.7
                start = int(ip_address(unicode(start_address)))
                end   = int(ip_address(unicode(end_address)))
            return [ip_address(ip).exploded for ip in range(start, end + 1)]

        for host in hosts:
            if '-' in host and not host.startswith('-'):
                start, end = host.strip().split('-')
                try:
                    reworked_hosts.extend(ips(start, end))
                except ValueError:
                    raise Exception("Range of ip_addresses isn't valid")
            else:
                reworked_hosts.append(host)
        return reworked_hosts

    def exists_hostname(self, existing_hosts, hostname):
        return hostname in existing_hosts.keys()

    def exists_ip(self, existing_hosts, ip):
        for host_opts in existing_hosts.values():
            if ip == self.get_ip_from_opts(host_opts):
                return True
        return False

    def delete_host_by_ip(self, existing_hosts, ip):
        for hostname, host_opts in existing_hosts.items():
            if ip == self.get_ip_from_opts(host_opts):
                del existing_hosts[hostname]
                return
        raise ValueError("Unable to find host by IP: {0}".format(ip))

    def purge_invalid_hosts(self, hostnames, protected_names=[]):
        for role in self.yaml_config['all']['children']:
            if role != 'lokum-cluster' and self.yaml_config['all']['children'][role]['hosts']:  # noqa
                all_hosts = self.yaml_config['all']['children'][role]['hosts'].copy()  # noqa
                for host in all_hosts.keys():
                    if host not in hostnames and host not in protected_names:
                        self.debug(
                            "Host {0} removed from role {1}".format(host, role))  # noqa
                        del self.yaml_config['all']['children'][role]['hosts'][host]  # noqa
        # purge from all
        if self.yaml_config['all']['hosts']:
            all_hosts = self.yaml_config['all']['hosts'].copy()
            for host in all_hosts.keys():
                if host not in hostnames and host not in protected_names:
                    self.debug("Host {0} removed from role all".format(host))
                    del self.yaml_config['all']['hosts'][host]

    def add_host_to_group(self, group, host, opts=""):
        self.debug("adding host {0} to group {1}".format(host, group))
        if group == 'all':
            if self.yaml_config['all']['hosts'] is None:
                self.yaml_config['all']['hosts'] = {host: None}
            self.yaml_config['all']['hosts'][host] = opts
        elif group != 'lokum-cluster:children':
            if self.yaml_config['all']['children'][group]['hosts'] is None:
                self.yaml_config['all']['children'][group]['hosts'] = {
                    host: None}
            else:
                self.yaml_config['all']['children'][group]['hosts'][host] = None  # noqa

    def add_var_to_group(self, group, var, opts=""):
        self.debug("adding var {0} to group {1}".format(var, group))
        if group == 'all':
            self.yaml_config['all']['vars'][var] = str(opts)
        else:
            self.yaml_config['all']['children'][group]['vars'][var] = str(opts)

    def set_docker(self, hosts, vars = None):
        self.add_host_to_group('docker-swarm-manager', hosts[0])
        for host in hosts:
            self.add_host_to_group('docker-swarm-worker', host)
        docker = {'children': {'docker-swarm-manager': None, 'docker-swarm-worker': None}}
        self.yaml_config['all']['children']['docker'] = docker

    def set_glusterfs(self, hosts, vars = None):
        self.add_host_to_group('glusterfs-primary', hosts[0])
        for host in hosts:
            self.add_host_to_group('glusterfs-second', host)
        glusterfs = {'children': {'glusterfs-primary': None, 'glusterfs-second': None}}
        self.yaml_config['all']['children']['glusterfs'] = glusterfs

    def set_minio(self, hosts, vars = None):
        self.add_host_to_group('minio-server', hosts[0])
        for host in hosts:
            self.add_host_to_group('minio-worker', host)
        minio = {'children': {'minio-server': None, 'minio-worker': None}}
        self.yaml_config['all']['children']['minio'] = minio

    def set_hadoop(self, hosts, vars = None):
        self.add_host_to_group('hadoop-namenode', hosts[0])
        self.add_host_to_group('hadoop-resourcemanager', hosts[0])
        for host in hosts:
            self.add_host_to_group('hadoop-datanode', host)
        hadoop = {'children': {'hadoop-namenode': None, 'hadoop-datanode': None}}
        self.yaml_config['all']['children']['hadoop'] = hadoop

    def set_spark(self, hosts, vars = None):
        self.add_host_to_group('spark-master', hosts[0])
        for host in hosts:
            self.add_host_to_group('spark-worker', host)
        spark = {'children': {'spark-master': None, 'spark-worker': None}}
        self.yaml_config['all']['children']['spark'] = spark

    def set_cassandra(self, hosts, vars = None):
        for host in list(self.hosts.keys())[:CASSANDRA_SEEDS_COUNT]:
            self.add_host_to_group('cassandra-seeds', host)
        for host in hosts:
            self.add_host_to_group('cassandra-nodes', host)
        cassandra = {'children': {'cassandra-seeds': None, 'cassandra-nodes': None}}
        self.yaml_config['all']['children']['cassandra'] = cassandra

    def set_jupyterhub(self, hosts, vars = None):
        if vars is not None:
            for var, opts in vars.items():
                self.add_var_to_group('jupyterhub', var, opts)
        self.add_host_to_group('jupyterhub', hosts[0])

    def set_dask(self, hosts, vars = None):
        self.add_host_to_group('dask-scheduler', hosts[0])
        for host in hosts:
            self.add_host_to_group('dask-worker', host)
        dask = {'children': {'dask-scheduler': None, 'dask-worker': None}}
        self.yaml_config['all']['children']['dask'] = dask

    def set_all(self, hosts, vars = None):
        if vars is not None:
            for var, opts in vars.items():
                self.add_var_to_group('all', var, opts)
        for host, opts in hosts.items():
            self.add_host_to_group('all', host, opts)

    def load_file(self, files=None):
        '''Directly loads JSON to inventory.'''

        if not files:
            raise Exception("No input file specified.")

        import json

        for filename in list(files):
            # Try JSON
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
            except ValueError:
                raise Exception("Cannot read %s as JSON, or CSV", filename)

            self.ensure_required_groups(ROLES)

            # self.set_lokum_cluster()

            for group, hosts in data.items():
                self.ensure_required_groups([group])
                for host, opts in hosts.items():
                    optstring = {'ansible_host': opts['ip'],
                                 'ip': opts['ip'],
                                 'access_ip': opts['ip']}
                    self.add_host_to_group('all', host, optstring)
                    self.add_host_to_group(group, host)
            self.write_config(self.config_file)

    def parse_command(self, command, args=None):
        if command == 'help':
            self.show_help()
        elif command == 'print_cfg':
            self.print_config()
        elif command == 'print_ips':
            self.print_ips()
        elif command == 'load':
            self.load_file(args)
        else:
            raise Exception("Invalid command specified.")

    def show_help(self):
        help_text = '''Usage: inventory.py ip1 [ip2 ...]
Examples: inventory.py 10.10.1.3 10.10.1.4 10.10.1.5

Available commands:
help - Display this message
print_cfg - Write inventory file to stdout
print_ips - Write a space-delimited list of IPs from "all" group

Advanced usage:
Add another host after initial creation: inventory.py 10.10.1.5
Add range of hosts: inventory.py 10.10.1.3-10.10.1.5
Add hosts with different ip and access ip: inventory.py 10.0.0.1,192.168.10.1 10.0.0.2,192.168.10.2 10.0.0.3,192.168.10.3
Delete a host: inventory.py -10.10.1.3
Delete a host by id: inventory.py -node1

Configurable env vars:
DEBUG                   Enable debug printing. Default: True
CONFIG_FILE             File to write config to Default: ./hosts.yaml
HOST_PREFIX             Host prefix for generated hosts. Default: node
'''  # noqa
        print(help_text)

    def print_config(self):
        yaml.dump(self.yaml_config, sys.stdout)

    def print_ips(self):
        ips = []
        for host, opts in self.yaml_config['all']['hosts'].items():
            ips.append(self.get_ip_from_opts(opts))
        print(' '.join(ips))


def main(argv=None):
    if not argv:
        argv = sys.argv[1:]
    MarzipanInventory(argv, CONFIG_FILE)


if __name__ == "__main__":
    sys.exit(main())
