#!/usr/bin/env python3
import sys
import os
import subprocess
import time
from Marzipan.marzipan import deploy_cluster
import inventory_builder.inventory as invb

os.chdir("/marzipan")

rc = subprocess.run(["mkdir","-p","/marzipan/deployments/tmp"])
rc = subprocess.run("/marzipan/marzipan_scripts/generate_keys.sh")

try:
	surfone = deploy_cluster()	
except:
	print('An unexpected error occurred:', sys.exc_info())
	if 'NAME is already taken by' in str(sys.exc_info()[1]):
		print('A cluster with your chosen name has already been \
			   instantiated and the template file exists. Please \
			   either choose a different name or remove the \
			   template in ONE')
		sys.exit()
	else:
		raise
	


#construct deployment path
deploymentFolder = surfone.config["cluster"]["basename"]+"-cluster"
deploymentFolderPath = "/marzipan/deployments/"+deploymentFolder

#check whether specified a cluster with the same name already exists (i.e if the specified path exists). If so, abort
if os.path.isdir(deploymentFolderPath):
	print('A Cluster with the same name has been instantiated before. \
		   Although is has been removed from ONE files remain present \
		   in the deployments sub-folder an will cause issues. \
		   Please remove these and run anew.')
	print('removing cluster and deleting created template...')
	surfone.wipe_cluster()
	print('Exiting...')
	sys.exit()

rc = subprocess.run(["mv","/marzipan/deployments/tmp",deploymentFolderPath])

#copy keys for emma compatability
rc = subprocess.run(["cp","-v",deploymentFolderPath+"/id_rsa_marzipan_ubuntu.key","/marzipan/emma/files/"+deploymentFolder+".key"])
rc = subprocess.run(["cp","-v",deploymentFolderPath+"/id_rsa_marzipan_ubuntu.key.pub","/marzipan/emma/files/"+deploymentFolder+".key.pub"])
rc = subprocess.run(["cp","-v",deploymentFolderPath+"/id_rsa_marzipan_ubuntu.key","/marzipan/emma/files/hadoop_id_rsa"])
rc = subprocess.run(["cp","-v",deploymentFolderPath+"/id_rsa_marzipan_ubuntu.key.pub","/marzipan/emma/files/hadoop_id_rsa.pub"])


CONFIG_FILE = deploymentFolderPath+'/hosts.yaml'
invb.HOST_PREFIX = surfone.config["cluster"]["basename"]
invb.DEBUG = True

from inventory_builder.inventory import MarzipanInventory

MarzipanInventory(surfone.cluster_vm_ips, CONFIG_FILE)

time.sleep(10)

print("run provisioning with ansible here")

"""
Marzipan ansiible palybooks and steps.
These mirror those established in lokum
"""

#copy ssh keys
ansible_ssh_command = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -b --become-user=root -i "+CONFIG_FILE+" -e cluster="+deploymentFolder+" /marzipan/marzipan_ansible/ansible_playbooks/set_ssh_keys.yml --private-key="+deploymentFolderPath+"/id_rsa_marzipan_root.key -v -c paramiko"
print(ansible_ssh_command)
os.system(ansible_ssh_command)

#update hosts.yaml file
ansible_update_hosts_command = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -b --become-user=root -i "+CONFIG_FILE+" -e cluster="+deploymentFolder+" /marzipan/marzipan_ansible/ansible_playbooks/update_hosts_file.yml --private-key="+deploymentFolderPath+"/id_rsa_marzipan_root.key -v -c paramiko"
print(ansible_update_hosts_command)
os.system(ansible_update_hosts_command)

#configure fire wall
ansible_firewall_command = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -b --become-user=root -i "+CONFIG_FILE+" -e cluster="+deploymentFolder+" /marzipan/marzipan_ansible/ansible_playbooks/firewall.yml --private-key="+deploymentFolderPath+"/id_rsa_marzipan_root.key -v -c paramiko"
print(ansible_firewall_command)
os.system(ansible_firewall_command)

#ping hosts as root
#ansible_ping_as_root_command = "ANSIBLE_HOST_KEY_CHECKING=False; cd /marzipan ; ansible all -b --become-user=root -i "+CONFIG_FILE+" -e cluster="+deploymentFolder+" -m ping --private-key="+deploymentFolderPath+"/id_rsa_marzipan_root.key -vvv"
#print(ansible_ping_as_root_command)
#os.system(ansible_ping_as_root_command)

#ping hosts as ubuntu
#ansible_ping_as_ubuntu_command = "ANSIBLE_HOST_KEY_CHECKING=False; cd /marzipan ; ansible all -b --become-user=ubuntu -i "+CONFIG_FILE+" -e cluster="+deploymentFolder+" -m ping --private-key="+deploymentFolderPath+"/id_rsa_marzipan_ubuntu.key -vvv "
#print(ansible_ping_as_ubuntu_command)
#os.system(ansible_ping_as_ubuntu_command)

"""
emma based provisioninig 
"""

#prepare cloud
ansible_prep_cloud_command = "ANSIBLE_HOST_KEY_CHECKING=False; cd /marzipan/emma; ansible-playbook -i "+CONFIG_FILE+" -e datadisk=/dev/vdb -e host_name="+deploymentFolderPath+"/id_rsa_marzipan_ubuntu prepcloud-playbook.yml --private-key="+deploymentFolderPath+"/id_rsa_marzipan_ubuntu.key -v -c paramiko"
print(ansible_prep_cloud_command)
os.system(ansible_prep_cloud_command)


#install platform (light)
ansible_install_platform_command = "ANSIBLE_HOST_KEY_CHECKING=False; cd /marzipan/emma/vars; sh ./create_vars_files.sh; cd /marzipan/emma; ansible-playbook -i "+CONFIG_FILE+" --extra-vars CLUSTER_NAME="+deploymentFolder+" install_platform_light.yml --tags 'common, extra_python_packages, gdal, dask' --skip-tags 'minio, hadoop, spark, jupyterhub,pdal,geotrellis,cassandra,geomesa' --private-key="+deploymentFolderPath+"/id_rsa_marzipan_ubuntu.key -v"
print(ansible_install_platform_command)
os.system(ansible_install_platform_command)

