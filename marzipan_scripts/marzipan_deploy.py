#!/usr/bin/env python3
import os
import subprocess
from Marzipan.marzipan import deploy_cluster
import inventory_builder.inventory as invb

os.chdir("/marzipan")

rc = subprocess.run(["mkdir","-p","/marzipan/deployments/tmp"])
rc = subprocess.run("/marzipan/marzipan_scripts/generate_keys.sh")

surfone = deploy_cluster()

#construct command
deploymentFolder = surfone.config["cluster"]["basename"]+"-cluster"
deploymentFolderPath = "/marzipan/deployments/"+deploymentFolder
rc = subprocess.run(["mv","/marzipan/deployments/tmp",deploymentFolderPath])

CONFIG_FILE = deploymentFolderPath+'/hosts.yaml'
invb.HOST_PREFIX = surfone.config["cluster"]["basename"]
invb.DEBUG = True

from inventory_builder.inventory import MarzipanInventory

MarzipanInventory(surfone.cluster_vm_ips, CONFIG_FILE)

print("run ansible here")
