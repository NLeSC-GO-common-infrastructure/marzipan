# marzipan
Automated (SURF HPC) OpenNebula instantiation and provisioning

## Usage
marzipan.py provides the `one_interface` class. The class' methods provide a high level interface to set up a cluster of VMs on the (SURFsara) OpenNebula cloud.

marzipan.py can be imported, poviding access to the class methods, or run as a script to fully automatedly set up a cluster of VMs.

marzipan is complemented by a `ClusterConf.ini` file, where the user can set desired configuration values such as the number of nodes, the name of the VMs, the OpenNebula endpoint and their credentials. The repository includes a file `ClusterConf.ini.example` which can be appropriately modified and subsequnetly renamed.

Furthermore, the user should supply a template file specifying the desired VM configuration. An example, `opennebula_goera.tpl`, is provided in the repository. Please bear in mind, that the base image for the OS disk must be made available for the user (with the credentials beiing used) before executing marzipan.

Finally, the user can provide a public ssh key file for the `root` user to be included with the template. Alternatively, the ssh key can be supplied in the `ClusterConf.ini` file.

When run as a script, mazipan will construct a VM template in OpenNebula, and deploy the requested number of VMs based on this template. marzipan will monitor the deployment, only reporting successful execution when all VMs are in the `RUNNING` LCM_STATE. If this has failed to complete after 120 seconds marziopan will exit, notifying the user of failure.


## Reference/Documentation

[OpenNebula 5.2 Documentation for the XML-RPC API][http://docs.opennebula.io/5.2/integration/system_interfaces/api.html#actions-for-templates-management]

[PYONE bindings documentation][http://docs.opennebula.io/5.12/integration/system_interfaces/python.html]
