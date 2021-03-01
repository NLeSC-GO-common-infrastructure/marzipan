# ClusterConf.ini configuration file

The `ClusterConf.ini` file allows the user to set configuration parameters for instantiating a (cluster of) VM(s) on bare metal using the OpenNebula platform.

The parameters to be supplied are divided into three setions:

## one (OpenNebula)
This section covers access to the OpenNebula platform. The user should specify the endpoint, as well as their login credentials. __Note__: Please set access to the ClusterConf.ini file at an appropriate level (e.g. `chmod 600`). DO NOT push this file to a remote repository. The `.gitignore` file currently precludes this happening. 

## ssh
This section specifies the path to the root public ssh key to be added to each VM created. The current setting:
```
root_public_key = /marzipan/deployments/tmp/id_rsa_marzipan_root.key.pub
```
ensures comaptibility with the automatic deployment options. The user may modify this HOWEVER, they are then responsible for ensuring compatability with the automatic deployment opions if desired.

## cluster
This section specifies which template file should be used and how many VM(s) will be created. Please ensure that he specifed templaye exists.
VM(s) will be named using the `basename` supplied with a numerial suffix starting at `1`
