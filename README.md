<!---
.. list-table::
   :widths: 25 25
   :header-rows: 1

   * - fair-software.nl recommendations
     - Badges
   * - \1. Code repository
     - |GitHub Badge|
   * - \2. License
     - |License Badge|
   * - \3. Community Registry
     - |Research Software Directory Badge|
   * - \4. Enable Citation
     - |Zenodo Badge|
   * - \5. Checklist
     - |CII Best Practices Badge|
   * - **Other best practices**
     -
   * - Continuous integration
     - |Python Build| |PyPI Publish|

.. |GitHub Badge| image:: https://img.shields.io/badge/github-repo-000.svg?logo=github&labelColor=gray&color=blue
   :target: https://github.com/NLeSC-GO-common-infrastructure/marzipan
   :alt: GitHub Badge

.. |License Badge| image:: https://img.shields.io/github/license/NLeSC-GO-common-infrastructure/stac2webdav
   :target: https://github.com/NLeSC-GO-common-infrastructure/marzipan
   :alt: License Badge

.. |Research Software Directory Badge| image:: https://img.shields.io/badge/rsd-marzipan-00a3e3.svg
   :target: https://www.research-software.nl/software/marzipan
   :alt: Research Software Directory Badge

..
    Goto https://zenodo.org/account/settings/github/ to enable Zenodo/GitHub integration.
    After creation of a GitHub release at https://github.com/NLeSC-GO-common-infrastructure/marzipan/releases
    there will be a Zenodo upload created at https://zenodo.org/deposit with a DOI, this DOI can be put in the Zenodo badge urls.
    In the README, we prefer to use the concept DOI over versioned DOI, see https://help.zenodo.org/#versioning.
.. |Zenodo Badge| image:: https://zenodo.org/badge/DOI/< replace with created DOI >.svg
   :target: https://doi.org/<replace with created DOI>
   :alt: Zenodo Badge

..
    A CII Best Practices project can be created at https://bestpractices.coreinfrastructure.org/en/projects/new
.. |CII Best Practices Badge| image:: https://bestpractices.coreinfrastructure.org/projects/< replace with created project identifier >/badge
   :target: https://bestpractices.coreinfrastructure.org/projects/< replace with created project identifier >
   :alt: CII Best Practices Badge
--->


## Badges

| fair-software.nl recommendations | Badge |
|:-|:-:|
| [1. Code Repository](https://fair-software.nl/recommendations/repository) | [![GitHub](https://img.shields.io/github/last-commit/NLeSC-GO-common-infrastructure/marzipan)](https://img.shields.io/github/last-commit/NLeSC-GO-common-infrastructure/marzipan) |
| [2. License](https://fair-software.nl/recommendations/license) | [![License](https://img.shields.io/github/license/NLeSC-GO-common-infrastructure/marzipan)]((https://img.shields.io/github/license/NLeSC-GO-common-infrastructure/marzipan)) |
| [3. Community Registry](https://fair-software.nl/recommendations/registry) | [![Research Software Directory](https://img.shields.io/badge/rsd-marzipan-00a3e3.svg)](https://www.research-software.nl/software/marzipan) |
| [4. Enable Citation](https://fair-software.nl/recommendations/citation) | [![DOI](https://zenodo.org/badge/DOI/< replace with created DOI >.svg)](https://doi.org/<replace with created DOI>) |
| [5. Code Quality Checklist](https://fair-software.nl/recommendations/checklist) | [![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/3754/badge)](https://bestpractices.coreinfrastructure.org/projects/3754)  |


# marzipan
Automated instantiation and deployment of (clusters of) virtual machine(s) on bare metal using the OpenNebula platform, as well as subsequent provisioning and deployment of services incl., e.g. Dask.

`marzipan` consists of the core `marzipan.py` python [module](https://github.com/NLeSC-GO-common-infrastructure/marzipan/tree/improve-documentation/Marzipan) providing a high level interface to the OpenNebula cloud,
as well as an accompanying [Docker framework](https://github.com/NLeSC-GO-common-infrastructure/marzipan/tree/improve-documentation/Docker) and configurable [deployment scripts](https://github.com/NLeSC-GO-common-infrastructure/marzipan/tree/improve-documentation/marzipan_scripts) providing a fully automated instantiation and provisioning environment.

For provisioning marzipan makes use of the [`emma_marzipan` fork](https://github.com/NLeSC-GO-common-infrastructure/emma/tree/emma_marzipan) ansible playbooks.

`marzipan` is based off and strongly draws from [`Lokum`](https://github.com/NLeSC/lokum), but is updated to make use of current versions of Ansible as well as python 3, and circumvents recurrent synchronicity and timeout issues arsing from the interplay of terraform, the runtastic OpenNebula provider for terraform, and various (legacy) OpenNebula versions.

`marzipan` has been tested on the SURFsara HPC cloud, but should work for any OpenNebula platform.

## Technologies and tools

- [OpenNebula](https://opennebula.io)
- [Docker](https://www.docker.com)
- [Ansible](https://www.ansible.com)
- [emma_marzipan fork](https://github.com/NLeSC-GO-common-infrastructure/emma/tree/emma_marzipan) of [emma](https://github.com/nlesc-sherlock/emma)



## Usage

### 1 Clone repository
To make use of `marzipan` the user should clone this repository to their local system. Further instructions on the use of `marzipan` assume a full replica of the repository on the users local system.

### 2 Adjust configuration and template
The user should modify the `ClusterConf.ini` file located in the [`config`]() subdirectory, as well as the `opennebula_goera.tpl` file in the [`templates`]() subdirectory to match their requirements.

#### 2.1 configuration
The `ClusterConf.ini` file enables the user to set desired configuration values such as the number of nodes, the name of the VMs, the OpenNebula endpoint and their credentials.
The [`config`](https://github.com/NLeSC-GO-common-infrastructure/marzipan/tree/improve-documentation/config) subdirectory of the repository includes a file `ClusterConf.ini.example` which can be appropriately modified and subsequently renamed.

#### 2.2 template
The user must supply a template file specifiying the desired configuration for the VM(s) to be created.
An example, `opennebula_goera.tpl`, is provided in the [`templates`](https://github.com/NLeSC-GO-common-infrastructure/marzipan/tree/improve-documentation/templates) subfolder of the repository.
In particular, the following fields will require modification:
```
CONTEXT = [
	GROUP = "your_group"]
DISK = [
    DATASTORE = "nameOfYourBaseImageDataStore"
    DATASTORE_ID = "IDOfYourBaseImageDataStore"
	IMAGE_ID ="IDOfYourBaseImage"
]
```

Please bear in mind, that the base image for the OS disk must be made available for the user (with the credentials being used) before executing `marzipan`. This is up to the user and can be accomplished using the OpenNebula user interface.


### 3 Build Docker image
Change directories to the [`Docker`](https://github.com/NLeSC-GO-common-infrastructure/marzipan/tree/improve-documentation/Docker) subdirectory.
Build the `nlesc/marzipan` docker image by running
```bash
./build_marzipan.sh
```
This creates the image with tag set to `latest`.

### 4 Run Docker framework to instantiate and provision a (cluster of) VM(s)
Change back to the root directory of the repository.
The docker framework can then be used to instantiate and provision a cluster of VMs by running
```bash
./deployCluster.sh
```
. The `root` and `ubuntu` user ssh keys generated for the cluster, as well as the `hosts.yaml` file enabling provisioning with the `emma` platform leveraging `ansible` are written to the `deployments` subdirectory (is created on execution) in a subfolder with the clusters name. They can be used to subsequently interact with the cluster.

The user can adapt the provisioning by modifying the `marzipan_deploy.py` script in the `marzipan_scripts` subdirectory in the section below
```
"""
emma based provisioninig 
"""
```
 The user is referred to the [`emma_marzipan` fork](https://github.com/NLeSC-GO-common-infrastructure/emma/tree/emma_marzipan) for supported options.

 __NOTE__: changes to the `marzipan_deploy.py` script require the [docker image](#3-build-docker-image) to be rebuilt before taking effect.


## Access to the cluster
The cluster VMs can be accesed via ssh as `ubuntu` or `root` user, using the generated keys. For example:
```bash
ssh -i ./deployments/<clustername>/id_rsa_marzipan_root.key root@SERVER_IP
or
ssh -i ./deployments/<clustername>/id_rsa_marzipan_ubuntu.key ubuntu@SERVER_IP
```


## The marzipan OpenNebula interface

The core `marzipan.py` module (located in the `Marzipan` subfolder) provides the `one_interface` class. The class' methods provide a high level interface to set up a cluster of VMs on the (SURFsara) OpenNebula cloud.

`marzipan.py` can be imported, providing access to the class methods, or run as a script to fully automatedly set up a cluster of VMs. `marzipan.py` also provides a high level class method `deploy_cluster()` which corresponds to the execution as a script.

`marzipan` is complemented by a `ClusterConf.ini` file (in `config`), where the user can set desired configuration values such as the number of nodes, the name of the VMs, the OpenNebula endpoint and their credentials. The repository includes a file `ClusterConf.ini.example` which can be appropriately modified and subsequently renamed.

Furthermore, the user should supply a template file specifying the desired VM configuration. An example, `opennebula_goera.tpl`, is provided in the `templates` subfolder of the repository. Please bear in mind, that the base image for the OS disk must be made available for the user (with the credentials being used) before executing `marzipan`.

Finally, the user can provide a public ssh key file for the `root` user to be included with the template. Alternatively, the ssh key can be supplied in the `ClusterConf.ini` file.
NOTE: if using the Docker framework, the use should refrain from, or take great care in, changing the settings relating to the ssh keys, as these are autogenerated during deployment.

When run as a script or by invoking the full deployment method `mazipan` will construct a VM template in OpenNebula, and deploy the requested number of VMs based on this template. `marzipan` will then monitor the deployment, only reporting successful execution when all VMs are in the `RUNNING` LCM_STATE. If this has failed to complete after 120 seconds marzipan will exit, notifying the user of failure.


## Reference/Documentation

[OpenNebula 5.2 Documentation for the XML-RPC API](http://docs.opennebula.io/5.2/integration/system_interfaces/api.html#actions-for-templates-management)

[PYONE bindings documentation](http://docs.opennebula.io/5.12/integration/system_interfaces/python.html)