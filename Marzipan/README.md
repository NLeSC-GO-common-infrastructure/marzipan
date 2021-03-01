# marzipan core module

The core `marzipan.py` module leverages the [PYONE]() python bindings to the OpenNebula XML-RPC API to provide higer level abstrations for the steps required in instantiating a (cluster of) VM(s) on bare metal using the OpenNebula platform

`marzipan.py` provides the `one_interface` class with methods enabling the creation, deletion, instantiation, and termination  of templates and virtual machines.
In additon, the module provides a function `deploy_cluster()` which can be called and will automatically handle spinning up a cluster as defined in the `ClusterConf.ini` and `opennebula_goera.tpl` configuration and template files.

Finally `marzipan.py` can also be run as a script invoking the `deploy_cluster()` function.

Further documentation is provided inline

## References/Documentation

[OpenNebula 5.2 Documentation for the XML-RPC API](http://docs.opennebula.io/5.2/integration/system_interfaces/api.html#actions-for-templates-management)

[PYONE bindings documentation](http://docs.opennebula.io/5.12/integration/system_interfaces/python.html)
