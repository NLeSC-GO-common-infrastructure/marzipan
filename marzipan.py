import pyone
import getpass
import configparser
import os
import time

class one_interface(object):

    def __init__(self):
        self.config = None
        self.client = None
        self.root_public_key = None
        self.template = None
        self.template_id = None
        self.cluster_vm_ids = []

    def get_config(self):
        Config = configparser.ConfigParser()
        Config.read('ClusterConf.ini')
        self.config = Config

    def get_one_server(self):
        uname = self.config['one']['username']
        pwd = self.config['one']['password']
        endpoint = self.config['one']['endpoint']
        one_server = pyone.OneServer(endpoint, session = uname+':'+pwd)
        self.client = one_server

    def get_public_key(self):
        if os.path.isfile(self.config['ssh']['root_public_key']):
            with open(self.config['ssh']['root_public_key'],'r') as keyfile:
                self.root_public_key = keyfile.read().rstrip('\n')
        else:
            self.root_public_key = self.config['ssh']['root_public_key']

    def get_template(self):
        with open(self.config['cluster']['VMtemplate'],'r') as templatefile:
            template = templatefile.read()
        self.template = "NAME = "+self.config['cluster']['basename']+"\n"+template.replace('replace_root_key',self.root_public_key)

    def create_one_template(self):
        self.client.template.allocate(self.template)
        n_templates = len(self.client.templatepool.info(-1,-1,-1).VMTEMPLATE)
        for i in range(n_templates):
            template = self.client.templatepool.info(-1,-1,-1).VMTEMPLATE[i]
            if template.NAME == self.config['cluster']['basename']:
                self.template_id = template.ID
            else:
                pass

    def create_one_vm(self,counter):
        vm_name=self.config['cluster']['basename']+str(counter)
        vm_id = self.client.template.instantiate(self.template_id,vm_name)
        return vm_id

    def create_one_vm_cluster(self):
        for j in range(int(self.config['cluster']['numberVMs'])):
            vmj_id = self.create_one_vm(j)
            self.cluster_vm_ids.append(vmj_id)

    def monitor_cluster_vm_states(self):
        targetstates = [3 for i in range(int(self.config['cluster']['numberVMs']))]
        targetlcmstates = targetstates
        states = [0 for i in range(int(self.config['cluster']['numberVMs']))]
        lcmstates = [0 for i in range(int(self.config['cluster']['numberVMs']))]
        inprogress=1
        tzero = time.time()
        while inprogress == 1:
            for i, vmid in enumerate(self.cluster_vm_ids):
                state = self.client.vm.info(vmid).STATE
                lcmstate = self.client.vm.info(vmid).LCM_STATE
                states[i] = state
                lcmstates[i] = lcmstate
            if states == targetstates and lcmstates == targetlcmstates :
                inprogress = 0
                print('All cluster VMs in state RUNNING')
            else:
                wait(10)
                print('Cluster initialization in progress...')
                elapsed_time = time.time() - tzero
                print('elapsed time : ',elapsed_time)
                if elapsed_time > 120. :
                    print('Something seems to have gone wrong during intialization...')
                    print('states: ', states)
                    print('lcmstates: ', lcmstates)
                    inprogress = 0

def main():

    surfone = one_interface()
    surfone.get_config()
    surfone.get_public_key()
    surfone.get_template()
    surfone.get_one_server()
    surfone.create_one_template()
    surfone.create_one_vm_cluster()
    surfone.monitor_cluster_vm_states()



if __name__ == '__main__':
    main()
