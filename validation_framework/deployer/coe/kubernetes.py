import logging
import invoke

from validation_framework.deployer.coe import COEBase
from validation_framework.common.nuvla_uuid import NuvlaUUID
from validation_framework.deployer.target_device.ssh_target import SSHTarget
from validation_framework.deployer.target_device.target import TargetDeviceConfig, TargetDevice
from validation_framework.common import constants as cte
from fabric import Result
import json
import time
from threading import Event, Thread
import re
from pathlib import Path

logger: logging.Logger = logging.getLogger(__name__)


class KubernetesCOE(COEBase):

    def __init__(self, device_config: TargetDeviceConfig, **kwargs):
        self.engine_folder: str = ''
        self.device = SSHTarget(device_config)
        self.nuvla_uuid = ''
        self.namespace = ''
        self.certificate_manager_pod = ''
        self.cred_check_thread: CertificateSignCheck = None
        super().__init__(self.device, logger, **kwargs)

    def start_engine(self,
                     uuid: NuvlaUUID,
                     remove_old_installation: bool = True,
                     extra_envs: dict = None):
        """
        Pulls the correct kubernetes image
        and then start the pods
        :param uuid:
        :param remove_old_installation:
        :param extra_envs:
        :return:
        """
        idparts = uuid.split('/')
        self.nuvla_uuid = idparts[1]
        add_repo_cmd = f'sudo helm repo add {cte.NUVLAEDGE_KUBE_LOCAL_REPO_NAME} {cte.NUVLAEDGE_KUBE_REPO}'
        result: Result = self.device.run_sudo_command(add_repo_cmd)
        if result.failed:
            self.logger.error(f'Could not add repo to helm {cte.NUVLAEDGE_KUBE_REPO}: {result.stderr}')
        version = "''" if self.nuvlaedge_version == '' else self.nuvlaedge_version
        install_image_cmd = cte.NUVLAEDGE_KUBE_INSTALL_IMAGE.format(
            uuid=self.nuvla_uuid,
            repo=cte.NUVLAEDGE_KUBE_LOCAL_REPO_NAME,
            chart=cte.NUVLAEDGE_KUBE_LOCAL_CHART_NAME,
            version=version,
            hostname=self.device.hostname
        )

        if self.include_peripherals:
            for peripheral in self.peripherals:
                cmd_arg = f' --set peripheralManager{peripheral}=true '
                install_image_cmd = install_image_cmd + cmd_arg

        envs_configuration: dict = self.engine_configuration.model_dump(by_alias=True)
        if extra_envs:
            envs_configuration.update(extra_envs)

        self.logger.info(f'Starting NuvlaEdge with UUID: {self.nuvla_uuid} with'
                         f' configuration: '
                         f'\n\n {json.dumps(envs_configuration, indent=4)} \n')
        self.device.run_sudo_command(install_image_cmd, envs=envs_configuration)

        self.namespace = self.__get_current_nuvlaedge_namespace_running()

        self.cred_check_thread = CertificateSignCheck(device_config=self.device.target_config,
                                                      namespace=self.namespace)
        self.cred_check_thread.start()

        self.logger.info('Device start command executed')

    def add_peripheral(self):
        pass

    def remove_peripheral(self):
        pass

    def stop_engine(self):
        self.purge_engine()

    def get_authorized_keys(self):
        return self.device.run_sudo_command("sudo cat /root/.ssh/authorized_keys")

    def get_engine_logs(self):
        self.logger.info(f'Retrieving Log files from engine run with UUID: {self.engine_configuration.nuvlaedge_uuid}')
        get_pods_cmd = (f'sudo kubectl get pods -n {self.namespace} -o json | '
                        'jq \'.items[] | {name: .metadata.name}\'')
        result: Result = self.device.run_sudo_command(get_pods_cmd)
        if result.failed or result.stdout == '':
            return

        # 1. Get all pods in the concerned namespace
        self.logger.debug(f'Extracting logs from: \n\n\t{result.stdout}\n')
        pods = json.loads(result.stdout)

        # 2. Iteratively copy logs from kubernetes pods
        #    to /tmp/<new_folder> and chmod before transferring it to the running machine
        self.device.run_sudo_command(
            f'sudo mkdir -p /tmp/{self.engine_configuration.compose_project_name}')
        local_tmp_path: Path = Path(f'/tmp/{self.engine_configuration.compose_project_name}')
        local_tmp_path.mkdir(parents=True, exist_ok=True)

        for pod in pods:
            pod_name = pod.get("name")
            get_logs_cmd = (f'sudo kubectl logs -n {self.namespace} {pod_name} >> '
                            f'/tmp/{self.engine_configuration.compose_project_name}/{pod_name}.log')
            self.device.run_sudo_command(get_logs_cmd)

            self.device.download_remote_file(remote_file_path=f'/tmp/{pod_name}.log',
                                             local_file_path=local_tmp_path / (pod_name + '.log'))

    def get_container_logs(self, container):
        pass

    def get_coe_type(self):
        return "kubernetes"

    def engine_running(self) -> bool:
        check_pods_cmd = f'sudo kubectl get pods -n {self.namespace} --no-headers'
        result: Result = self.device.run_sudo_command(check_pods_cmd)
        if result.failed or result.stdout.__contains__('No resources found'):
            return False
        return True

    def remove_engine(self):
        self.purge_engine()

    def peripherals_running(self, peripherals: set) -> bool:
        get_all_pods_running_cmd = (f'sudo kubectl get -n {self.namespace} pods -o json | '
                                    'jq \'.items[] | select(.status.phase == "Running") | '
                                    '.metadata.name | select(contains("peripheral-manager"))\'')

        result: Result = self.device.run_sudo_command(get_all_pods_running_cmd)
        if result.failed or result.stdout == '':
            return False

        list_pods = result.stdout.strip().split('\n')
        pattern = 'peripheral-manager-([a-z]+)-deployment.+'
        for pod in list_pods:
            pod = pod.strip().replace('"', '')
            res = re.search(pattern, pod)
            if peripherals.__contains__(res.group(1)):
                peripherals.remove(res.group(1))
        return not bool(peripherals)

    def purge_engine(self):
        """
            This will remove all pods and namespaces for kubernetes
        :return:
        """
        self.logger.info(f'Purging engine in device {self.device}')
        if self.cred_check_thread is not None:
            self.logger.info("Waiting for credentials check thread to close")
            self.cred_check_thread.join(50)

        self.logger.info(f'Purging engine in device {self.device}')
        namespaces_running = self.__get_namespaces_running()
        commands: list = ['sudo kubectl delete clusterrolebindings.rbac.authorization.k8s.io '
                          'nuvla-cluster-role-binding nuvlaedge-service-account-cluster-role-binding']

        for namespace in namespaces_running:
            if namespace.__contains__('kube') or namespace == 'default':
                continue
            commands.append(f'sudo kubectl delete ns {namespace}')
            commands.append(f'sudo helm uninstall {namespace}')

        for cmd in commands:
            try:
                self.device.run_sudo_command(cmd)
            except invoke.exceptions.UnexpectedExit as ex:
                self.logger.error(f'Unexpected exit on command {cmd} : Exception : {ex}')
            except Exception as ex:
                self.logger.error(f'Unable to run commands on {self.device} {ex}')

    def __get_current_nuvlaedge_namespace_running(self):
        get_curr_nuvlaedge_namespace_cmd = ('sudo kubectl get namespaces -o json | jq '
                                            '\'.items[].metadata.labels."kubernetes.io/metadata.name"'
                                            f' | select(contains("{self.nuvla_uuid}"))\'')
        result: Result = self.device.run_sudo_command(get_curr_nuvlaedge_namespace_cmd)
        namespaces = result.stdout.split('\n')
        namespace = namespaces[0].replace('"', '')
        return namespace

    def __get_namespaces_running(self) -> []:
        get_nuvla_namespaces_cmd = ('sudo kubectl get namespaces -o json | jq '
                                    '\'.items[].metadata.labels."kubernetes.io/metadata.name"\'')
        result: Result = self.device.run_sudo_command(get_nuvla_namespaces_cmd)
        namespaces = result.stdout
        list_namespaces = namespaces.split('\n')

        output = []
        for namespace in list_namespaces:
            if namespace:
                output.append(namespace.replace('"', ''))
        running_namespaces = ' '.join([str(item) for item in output])
        self.logger.debug(f'Current namespaces running {running_namespaces}')
        return output


def get_pod_name(device: TargetDevice, namespace, app_name, status: str = 'Running'):
    get_pod_cmd = (f'sudo kubectl get -n {namespace} pods -o json |'
                   f' jq \'.items[] | select(.status.phase == "{status}") | '
                   f'.metadata.name | select(contains("{app_name}"))\'')
    result: Result = device.run_sudo_command(get_pod_cmd)
    if result.failed or result.stdout == '':
        return ''
    list_names = result.stdout.strip().split('\n')
    return list_names[0].replace('"', '')


def get_environmental_value(device, namespace, pod_name, key):
    get_pod_details = f'sudo kubectl get pod -n {namespace} {pod_name} -o json'
    result: Result = device.run_sudo_command(get_pod_details)
    if result.failed or result.stdout == '':
        logger.warning(f'Unable to get details of the pod {pod_name} in namespace {namespace}')
        return ''
    json_output = json.loads(result.stdout)
    container_info_list: list = json_output["spec"]["containers"]
    for container_info in container_info_list:
        env_list: list = container_info["env"]
        for envs in env_list:
            if envs["name"] == key:
                return envs["value"]
    logger.error(f'Key {key} not present in {pod_name}')


class CertificateSignCheck(Thread):
    def __init__(self, device_config: TargetDeviceConfig, namespace):
        super(CertificateSignCheck, self).__init__()
        self.device = SSHTarget(device_config)
        self.exit_event: Event = Event()
        self.namespace = namespace

    def join(self, timeout: float | None = 0):
        logger.info('Exiting Certificate sign check thread')
        self.exit_event.set()
        super().join(timeout)

    def run(self):
        credentials_pod = ''
        while credentials_pod == '':
            credentials_pod = get_pod_name(self.device, self.namespace, cte.NUVLAEDGE_KUBE_CERTIFICATE_MANAGER)
            time.sleep(0.5)
        csr_name = get_environmental_value(self.device, self.namespace, credentials_pod,
                                           cte.NUVLAEDGE_KUBE_CSR_NAME_KEY)

        time_to_sleep = 2
        while not self.exit_event.is_set():
            if not self.device.is_reachable():
                self.exit_event.wait(30)
                continue
            get_csr_cmd = (f'sudo kubectl get certificatesigningrequests.certificates.k8s.io -o json | jq \'.items[] | '
                           f'select(.metadata.name == "{csr_name}") | '
                           '.status.conditions[0].type\'')
            self.exit_event.wait(time_to_sleep)

            result: Result = self.device.run_sudo_command(get_csr_cmd)
            if result.failed:
                continue

            status = result.stdout
            status = status.strip().replace('"', '')
            if status == "Approved":
                time_to_sleep = 5
                continue
            # approve certificate
            approve_csr_cmd = f'sudo kubectl certificate approve {csr_name}'
            try:
                self.device.run_sudo_command(approve_csr_cmd)
            except Exception as ex:
                logger.warning(f'Approval of csr command failed : {ex}')
            logger.info(f'Approved certificate {csr_name}')
