# Marzipan scripts

this subdirectory contains two helper scripts for the use of `marzipan` in automatically deploying a (cluster of) VM(s).

## `marzipan_deploy.py`
This is the `ENTRYPOINT` script for the Docker framework. It deals with the fully automated instantiation deployment and provisioning of the cluster, leveraging `marzipan` for the instantiation, ansible for futher set-up and `emma_marzipan` for the (software) provisioning. It also auto-generates ssh key pairs for the `root` and `ubuntu` users via the [`generate_keys.sh` script]().


## `generate_keys.sh`
This script generates pairs of SSH keys for the `ubuntu` and `root` users. and makes them available to be included in the VM(s) being spun up.
