import time

from pyVim.connect import SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import atexit

import config


KB = 1024
MB = 1024 * KB
GB = 1024 * MB

VIM_VIRTUAL_MACHINE = vim.VirtualMachine
VIM_DATA_STORE = vim.Datastore
VIM_DATA_CENTER = vim.Datacenter
VIM_CLUSTER = vim.ClusterComputeResource
VIM_RESOURCE_POOL = vim.ResourcePool
VIM_FOLDER = vim.Folder
VIM_HOST = vim.ComputeResource

VIM_TYPES = [
    VIM_VIRTUAL_MACHINE,
    VIM_DATA_STORE,
    VIM_DATA_CENTER,
    VIM_CLUSTER,
    VIM_RESOURCE_POOL,
    VIM_FOLDER,
    VIM_HOST,
]


class ConnectionErr(Exception):
    def __init__(self, message):
        self.message = message


class VSphereClient(object):
    def __init__(self, hostname, username, password):
        try:
            self.__si = SmartConnectNoSSL(
                host=hostname,
                user=username,
                pwd=password,
                port="443")
        except Exception as ex:
            print('Failed to connect to the vCenter: {}'.format(ex))
            raise ConnectionErr(
                'Failed to connect to \"{}\"'.format(hostname))
        atexit.register(Disconnect, self.__si)
        self.__content = self.__si.RetrieveContent()

    @property
    def content(self):
        return self.__content

    @property
    def default_datacenter(self):
        dcs = self.list_objects_by_type(VIM_DATA_CENTER)
        if len(dcs) > 0:
            return dcs[0]
        else:
            return None

    @property
    def default_cluster(self):
        clusters = self.list_objects_by_type(VIM_CLUSTER)
        if len(clusters) > 0:
            return clusters[0]
        else:
            return None

    def print_summary(self):
        for t in VIM_TYPES:
            objs = self.list_objects_by_type(t)
            print('{}:'.format(t._wsdlName))
            for obj in objs:
                print('\tname: \"{}\" \n\t\tobject: {}'.format(
                    obj.name, obj))

    def list_objects_by_type(self, vim_type):
        objs = []
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim_type], True)
        for o in container.view:
            objs.append(o)
        return objs

    def list_vms(self, prefix=None):
        vms = []
        objs = self.list_objects_by_type(VIM_VIRTUAL_MACHINE)
        for o in objs:
            if not prefix or o.name.startswith(prefix):
                vms.append(VirtualMachine(o))
        return vms

    def list_datastores(self, prefix=None):
        datastores = []
        objs = self.list_objects_by_type(VIM_DATA_STORE)
        for o in objs:
            if not prefix or o.name.startswith(prefix):
                datastores.append(Datastore(o))
        return datastores

    def find_by_name(self, vim_type, name):
        if not name:
            return None

        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim_type], True)
        for o in container.view:
            if o.name == name:
                return o

    def find_by_moid(self, vim_type, moid):
        if not moid:
            return None

        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim_type], True)
        for o in container.view:
            if o._moId == moid:
                return o

    def get_datastore_from_datastore_cluster(
            self, ds_cluster_name, vm_folder, resource_pool):
        pod = self.find_by_name(vim.StoragePod, ds_cluster_name)

        podsel = vim.storageDrs.PodSelectionSpec()
        podsel.storagePod = pod

        storage_spec = vim.storageDrs.StoragePlacementSpec()
        storage_spec.podSelectionSpec = podsel
        storage_spec.type = 'create'
        storage_spec.folder = vm_folder
        storage_spec.resourcePool = resource_pool

        vm_conf = vim.vm.ConfigSpec()
        storage_spec.configSpec = vm_conf

        try:
            rec = self.content.storageResourceManager.RecommendDatastores(
                storageSpec=storage_spec)
            rec_action = rec.recommendations[0].action[0]
            real_datastore_name = rec_action.destination.name
        except:
            raise Exception("Datastore recommendation failure")

        return self.find_by_name(VIM_DATA_STORE, real_datastore_name)

    @staticmethod
    def wait_for_task(task):
        """ wait for a vCenter task to finish """
        task_done = False
        while not task_done:
            if task.info.state == 'success':
                return task.info.result
            if task.info.state == 'error':
                print("There was an error {}".format(task))
                task_done = True
            time.sleep(1)

    def clone_vm(
            self,
            vm_template,
            vm_name,
            power_on=True,
            dc_name="",
            ds_name="",
            cluster_name="",
            rp_name="Resources",
            vm_folder_name="vm",
            dsc_name=""):
        if dc_name:
            datacenter = self.find_by_name(vim.Datacenter, dc_name)
        else:
            datacenter = self.default_datacenter

        if vm_folder_name:
            vm_folder = self.find_by_name(vim.Folder, vm_folder_name)
        else:
            vm_folder = datacenter.vmFolder

        # if None, get the first one
        if cluster_name:
            cluster = self.find_by_name(
                vim.ClusterComputeResource, cluster_name)
        else:
            cluster = self.default_cluster

        if rp_name:
            resource_pool = self.find_by_name(
                vim.ResourcePool, rp_name)
        elif cluster:
            resource_pool = cluster.resourcePool
        else:
            raise Exception("Resource pool not specified")

        if ds_name:
            # datastore has been specified
            datastore = self.find_by_name(vim.Datastore, ds_name)
        elif dsc_name:
            # datastore cluster has been specified
            datastore = self.get_datastore_from_datastore_cluster(
                dsc_name, vm_folder, resource_pool
            )
        else:
            # use the same datastore as the vm template
            datastore = self.find_by_name(
                vim.Datastore, vm_template.datastore[0].info.name)

        relocate_spec = vim.vm.RelocateSpec()
        relocate_spec.datastore = datastore
        relocate_spec.pool = resource_pool

        clone_spec = vim.vm.CloneSpec()
        clone_spec.location = relocate_spec
        clone_spec.powerOn = power_on

        print('Cloning VM to ...')
        print('\t Data Center  : \'{}\''.format(datacenter.name))
        print('\t VM Folder    : \'{}\''.format(vm_folder.name))
        print('\t Resource Pool: \'{}\''.format(resource_pool.name))
        print('\t Data store   : \'{}\''.format(datastore.name))
        task = vm_template.Clone(folder=vm_folder, name=vm_name,
                                 spec=clone_spec)
        self.wait_for_task(task)
        print('VM \'{}\' cloned!'.format(vm_name))


class VirtualMachine(object):
    def __init__(self, vm):
        self.__internal = vm

    @property
    def data(self):
        return self.__internal

    @property
    def moid(self):
        return self.__internal._moId

    @property
    def name(self):
        return self.__internal.name

    @property
    def power_state(self):
        return self.__internal.runtime.powerState

    @property
    def is_paused(self):
        return self.__internal.runtime.paused

    @property
    def host(self):
        return self.__internal.runtime.host

    @property
    def guest_name(self):
        return self.__internal.guest.guestFullName

    @property
    def cpu(self):
        return self.__internal.config.hardware.numCPU

    @property
    def memory_mb(self):
        return self.__internal.config.hardware.memoryMB

    def __repr__(self):
        return '{}' \
               '\n\t {}/{}MB' \
               '\n\t {}'.format(
                self.name,
                self.cpu,
                self.memory_mb,
                self.guest_name)


class Datastore(object):
    def __init__(self, ds):
        self.__internal = ds

    @property
    def data(self):
        return self.__internal

    @property
    def moid(self):
        return self.__internal._moId

    @property
    def name(self):
        return self.__internal.name

    @property
    def status(self):
        return self.__internal.overallStatus

    @property
    def accessible(self):
        return self.__internal.summary.accessible

    @property
    def capacity(self):
        return self.__internal.summary.capacity

    @property
    def free_space(self):
        return self.__internal.summary.freeSpace

    @property
    def host_ids(self):
        return [host.key._moId for host in self.__internal.host]

    @property
    def hosts(self):
        return [host.key for host in self.__internal.host]

    @property
    def vms(self):
        return [vm._moId for vm in self.__internal.vm]

    def __repr__(self):
        return '{} ' \
               '\n\tspace: {:.2f} GB / {:.2f}BG' \
               '\n\tstatus: {} (accessible:{})' \
               '\n\thosts: {}' \
               '\n\tvms: {}'.format(
                self.name,
                self.free_space/GB, self.capacity/GB,
                self.status, self.accessible,
                self.hosts, self.vms)


if __name__ == '__main__':
    conf = config.load_yml_conf('', 'vc-169')

    #print_vcenter_summary(content)

    # datastores = list_objects_by_type(content, [vim.Datastore])
    # for ds in [Datastore(ds) for ds in datastores]:
    #     if ds.name.startswith('rubrik_'):
    #         continue
    #     print(ds)

    # vms = list_objects_by_type(content, [vim.VirtualMachine])
    # for vm in [VirtualMachine(vm) for vm in vms]:
    #     print(vm)

    client = VSphereClient(
        hostname=conf['url'],
        username=conf['username'],
        password=conf['password']
    )

    datastores = client.list_datastores('rubrik_')
    for ds in datastores:
        if ds.accessible:
            continue

        ds_name = ds.name
        for h in ds.hosts:
            for d in h.datastore:
                if d._moId == ds.moid:
                    h.configManager.datastoreSystem.RemoveDatastore(ds.data)
                    print("Removed datastore {} from host {}".format(
                        ds_name, h.name
                    ))
