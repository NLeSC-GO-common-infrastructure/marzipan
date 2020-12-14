import pyone
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
        self.cluster_vm_ips = []

    def get_config(self):
        """
        Read configuration options from file
        """
        Config = configparser.ConfigParser()
        Config.read('config/ClusterConf.ini')
        self.config = Config

    def get_one_server(self):
        """
        Connect to OpenNebula server
        """
        uname = self.config['one']['username']
        pwd = self.config['one']['password']
        endpoint = self.config['one']['endpoint']
        one_client = pyone.OneServer(endpoint, session = uname+':'+pwd)
        self.client = one_client

    def get_public_key(self):
        """
        Read public ssh key for root user from file specified in config options
        or directly from config
        """
        if os.path.isfile(self.config['ssh']['root_public_key']):
            with open(self.config['ssh']['root_public_key'],'r') as keyfile:
                self.root_public_key = keyfile.read().rstrip('\n')
        else:
            self.root_public_key = self.config['ssh']['root_public_key']

    def get_template(self):
        """
        Read in VM template file. Add Name to template based on config and add SSH key
        """
        with open(self.config['cluster']['VMtemplate'],'r') as templatefile:
            template = templatefile.read()
        self.template = "NAME = "+self.config['cluster']['basename']+"\n"+template.replace('replace_root_key',self.root_public_key)

    def create_one_template(self):
        """
        Create OpenNebula VM template according to specifications
        """
        self.client.template.allocate(self.template)
        n_templates = len(self.client.templatepool.info(-1,-1,-1).VMTEMPLATE)
        for i in range(n_templates):
            template = self.client.templatepool.info(-1,-1,-1).VMTEMPLATE[i]
            if template.NAME == self.config['cluster']['basename']:
                self.template_id = template.ID
            else:
                pass

    def delete_one_template(self,temp_id=None,delete_all=False):
        """
        delete ONE template. defaults to created template and preserves linked images
        """
        if temp_id == None:
            temp_id = self.template_id

        self.client.template.delete(temp_id, delete_all)
        """
        success, out, errcode = self.client.template.delete(temp_id, delete_all)
        if success == True:
            print('sucsessfully deleted template ',temp_id, out)
        else:
            print('failed to delete template ', temp_id, out)
        """

    def create_one_vm(self,counter):
        """
        instantiate VMtemplate to VM
        """
        vm_name=self.config['cluster']['basename']+str(counter)
        vm_id = self.client.template.instantiate(self.template_id,vm_name)
        return vm_id

    def terminate_one_vm_hard(self,vm_id):
        """
        issue terminate hard command to VM
        """
        self.client.vm.action('terminate-hard',vm_id)
        """
        success,out,errcode = self.client.vm.action('terminate-hard',vm_id)
        if success == True:
            print('sucsessfully terminated vm ',vm_id, out)
        else:
            print('failed to terminate vm ', vm_id, out)
        """

    def terminate_one_vm_cluster_hard(self):
        """
        terminate cluster consisting of multiple VMs
        """
        for _ , vmj_id in enumerate(self.cluster_vm_ids):
            print('terminating vm ',vmj_id)
            self.terminate_one_vm_hard(vmj_id)


    def create_one_vm_cluster(self):
        """
        instantiate multiple VMs, i.e. a cluster
        """
        for j in range(int(self.config['cluster']['numberVMs'])):
            vmj_id = self.create_one_vm(j)
            vmj_ip = self.client.vm.info(vmj_id).TEMPLATE['NIC']['IP']
            self.cluster_vm_ids.append(vmj_id)
            self.cluster_vm_ips.append(vmj_ip)


    def serialize_one_vm_ips(self):
        """
        serialize list of vm ips to file as comma separated list on single line
        """
        fname = self.config['cluster']['basename']+'_IPs.dat'
        with open(fname,'w') as ips_file:
            for i, ip in enumerate(self.cluster_vm_ips):
                if i == len(self.cluster_vm_ips) -1:
                    ips_file.write(ip)
                else:
                    ips_file.write(ip+',')

    def monitor_cluster_vm_states(self):
        """
        monitor cluster VMs untill all reach state RUNNING
        """
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
                time.sleep(10)
                print('Waiting for cluster VMs ...')
                elapsed_time = time.time() - tzero
                print('elapsed time : ',elapsed_time)
                if elapsed_time > 120. :
                    print('Something seems to have gone wrong during intialization...')
                    print('states: ', states)
                    print('lcmstates: ', lcmstates)
                    inprogress = 0

    def wipe_cluster(self):
        """
        termnates cluster and deletes created template
        """
        self.terminate_one_vm_cluster_hard()
        self.delete_one_template()

def deploy_cluster():
    """
    Complete automated workflow to deploy VM cluster if running marzipan.py as script
    """
    print("initializing interface ...")
    surfone = one_interface()
    print("reading configuration file ...")
    surfone.get_config()
    print("retrieving publuc key ...")
    surfone.get_public_key()
    print("reading template ...")
    surfone.get_template()
    print("connecting to ONE server ...")
    surfone.get_one_server()
    print("creating template on ONE ...")
    surfone.create_one_template()
    print("instantiating cluster of VMs ...")
    surfone.create_one_vm_cluster()
    print("monitoring vm states ...")
    surfone.monitor_cluster_vm_states()
    print("serializing IPs ...")
    surfone.serialize_one_vm_ips()
    print("cluster IDs are : ")
    print(surfone.cluster_vm_ids)
    print("cluster IPs are : ")
    print(surfone.cluster_vm_ips)
    return surfone

def main():
    """
    Run automated deployment as externally called script
    """
    _ = deploy_cluster()

if __name__ == '__main__':
    main()
