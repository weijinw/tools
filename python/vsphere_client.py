from pyVim.connect import SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import atexit

import config


def create_vsphere_connection(hostname, username, password):
    si = SmartConnectNoSSL(
        host=hostname,
        user=username,
        pwd=password,
        port="443")
    atexit.register(Disconnect, si)
    return si


def load_vsphere_contents(vcc):
    return vcc.RetrieveContent()


def get_obj_by_name(content, vimtype, name):
    if not name:
        return None

    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            return c


def filter_vms_by_name(content, name):
    vms = []
    container = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.VirtualMachine], True)
    for c in container.view:
        if c.name.startswith(name):
            vms.append(c)
    return vms


def get_obj_by_id(content, vim_type, object_id):
    if not object_id:
        return None

    container = content.viewManager.CreateContainerView(
        content.rootFolder, vim_type, True)
    for c in container.view:
        if c._moId == object_id:
            return c


def list_objects_by_type(content, vim_type):
    """
    :param content: Returned by load_vsphere_contents
    :param vim_type:
        vim.Datacenter,
        vim.ClusterComputeResource,
        vim.Datastore,
        vim.ResourcePool,
        vim.Folder
    :return:
    """
    objs = []
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vim_type, True)
    for c in container.view:
        objs.append(c)
    return objs


def get_default_datacenter(content):
    dcs = list_objects_by_type(content, [vim.Datacenter])
    if len(dcs) > 0:
        return dcs[0]
    else:
        return None


def get_default_cluster(content):
    clusters = list_objects_by_type(content, [vim.ClusterComputeResource])
    if len(clusters) > 0:
        return clusters[0]
    else:
        return None


def wait_for_task(task):
    """ wait for a vCenter task to finish """
    task_done = False
    while not task_done:
        if task.info.state == 'success':
            return task.info.result

        if task.info.state == 'error':
            print("there was an error")
            task_done = True


def get_datastore_from_datastore_cluster(
        content, ds_cluster_name, vm_folder, resource_pool):
    pod = get_obj_by_name(content, [vim.StoragePod], ds_cluster_name)

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
        rec = content.storageResourceManager.RecommendDatastores(
            storageSpec=storage_spec)
        rec_action = rec.recommendations[0].action[0]
        real_datastore_name = rec_action.destination.name
    except:
        raise Exception("Datastore recommendation failure")

    return get_obj_by_name(
        content, [vim.Datastore], real_datastore_name)


def print_vcenter_summary(content):
    types = [
        vim.Datacenter,
        vim.ClusterComputeResource,
        vim.Datastore,
        vim.ResourcePool,
        vim.Folder
    ]
    for t in types:
        objs = list_objects_by_type(content, [t])
        print('{}:'.format(t._wsdlName))
        for obj in objs:
            print('\tname: \"{}\" \n\t\tobject: {}'.format(obj.name, obj))


def clone_vm(
        content,
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
        datacenter = get_obj_by_name(content, [vim.Datacenter], dc_name)
    else:
        datacenter = get_default_datacenter(content)

    if vm_folder_name:
        vm_folder = get_obj_by_name(content, [vim.Folder], vm_folder_name)
    else:
        vm_folder = datacenter.vmFolder

    # if None, get the first one
    if cluster_name:
        cluster = get_obj_by_name(
            content, [vim.ClusterComputeResource], cluster_name)
    else:
        cluster = get_default_cluster(content)

    if rp_name:
        resource_pool = get_obj_by_name(
            content, [vim.ResourcePool], rp_name)
    elif cluster:
        resource_pool = cluster.resourcePool
    else:
        raise Exception("Resource pool not specified")

    if ds_name:
        # datastore has been specified
        datastore = get_obj_by_name(content, [vim.Datastore], ds_name)
    elif dsc_name:
        # datastore cluster has been specified
        datastore = get_datastore_from_datastore_cluster(
            content, dsc_name, vm_folder, resource_pool
        )
    else:
        # use the same datastore as the vm template
        datastore = get_obj_by_name(
            content, [vim.Datastore], vm_template.datastore[0].info.name)

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
    task = vm_template.Clone(folder=vm_folder, name=vm_name, spec=clone_spec)
    wait_for_task(task)
    print('VM \'{}\' cloned!'.format(vm_name))


if __name__ == '__main__':
    conf = config.load_yml_conf(
        '/Users/weijin.wang/ws/.secrets/appflows.yml', 'vc-169')

    vcc = create_vsphere_connection(
        hostname=conf['url'],
        username=conf['username'],
        password=conf['password']
    )
    content = load_vsphere_contents(vcc)

    #print_vcenter_summary(content)

    datastores = list_objects_by_type(content, [vim.Datastore])
    for ds in datastores:
        print('Datastore \"{} {} {}\"'.format(ds.name, ds.overallStatus, ds.summary))
