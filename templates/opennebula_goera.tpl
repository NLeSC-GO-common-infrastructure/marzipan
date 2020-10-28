CONTEXT = [
  DNS_HOSTNAME = "YES",
  NETWORK = "YES",
  SSH_PUBLIC_KEY = "replace_root_key",
  USERNAME = "root",
  GROUP = "eratosthenes-uu"]
CPU = "4.0"
VCPU = "4"
DISK = [
  DATASTORE = "local_images_ssd",
  DATASTORE_ID = "104",
  IMAGE_ID = "25621",
  SIZE = "15360",
  TYPE = "fs"]
DISK = [
  DATASTORE =  "ceph",
  DATASTORE_ID = "106",
  FORMAT = "raw",
  SIZE = "71680",
  TARGET = "vdb",
  TYPE = "fs" ]
DISK = [
  DATASTORE = "local_system_ssd",
  DATASTORE_ID = "103",
  DISK_TYPE = "FILE",
  SIZE = "49152",
  TARGET = "vdc",
  TYPE = "swap"]
INPUTS_ORDER = ""
MEMORY = "32768"
MEMORY_UNIT_COST = "MB"
NIC = [
  NETWORK = "internet",
  NETWORK_UNAME = "oneadmin" ]
OS = [
  ARCH = "x86_64",
  BOOT = "" ]