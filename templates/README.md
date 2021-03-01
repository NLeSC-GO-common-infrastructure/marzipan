# VM template(s)

This subdirectory contains VM template configurations to be deployed on the OpenNebula platform.
An example is provided by `opennebula_goera.tpl`.

This template can and must be adapted according to the users needs. If renamed the path to the appropriate template must be set in the `ClusterConf.ini` config file.

Relevant sections that should be modified include
```
CONTEXT = [
  DNS_HOSTNAME = "YES",
  NETWORK = "YES",
  SSH_PUBLIC_KEY = "replace_root_key",
  USERNAME = "root",
  GROUP = "eratosthenes-uu"]
```
The group should be changed to the user's. __Note__ the `SSH_PUBLIC_KEY` is filled with a placeholder that filled by the automatically generated root public ssh key when using fully automatic deployment. Should the user wish deploy more manually this field can/should be modified.

```
DISK = [
  DATASTORE = "local_images_ssd",
  DATASTORE_ID = "104",
  IMAGE_ID = "25621",
  SIZE = "15360",
  TYPE = "fs"]
```
This specifies the OS disk. The user MUST ensure that a base image (e.g. and Ubuntu server) exists in the specified datastore of the OpenNebula Platform with the specified `IMAGE_ID`. The size corresponds to the OS partition.

```
DISK = [
  DATASTORE =  "ceph",
  DATASTORE_ID = "106",
  FORMAT = "raw",
  SIZE = "71680",
  TARGET = "vdb",
  TYPE = "fs" ]
```
This section specifies the local HDD of the VM.

```
DISK = [
  DATASTORE = "local_system_ssd",
  DATASTORE_ID = "103",
  DISK_TYPE = "FILE",
  SIZE = "49152",
  TARGET = "vdc",
  TYPE = "swap"]
```
This section defines a swap partition.


```
MEMORY = "32768"
MEMORY_UNIT_COST = "MB"
```
This specifies the VM's RAM allocation, anmd finally the following defines it's network connection. `NETWORK` and `NETWORK_UNAME` can be adpated, but this is not required.

```
NIC = [
  NETWORK = "internet",
  NETWORK_UNAME = "oneadmin" ]
```  

