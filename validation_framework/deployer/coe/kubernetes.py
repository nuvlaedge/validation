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


_KUBECONFIG_ENV = {"KUBECONFIG": "/etc/rancher/k3s/k3s.yaml"}

class KubernetesCOE(COEBase):
    
    def __init__(self, device_config: TargetDeviceConfig, **kwargs):
        self.namespaces_running = []
        self.engine_folder: str = ''
        self.device = SSHTarget(device_config)
        self.nuvla_uuid = ''
        self.namespace = ''
        self.certificate_manager_pod = ''
        self.cred_check_thread: CertificateSignCheck = None
        super().__init__(self.device, logging.getLogger(__name__), **kwargs)

        self.project_name: str = ''

    def start_engine(self,
                     uuid: NuvlaUUID,
                     remove_old_installation: bool = True,
                     project_name: str = cte.PROJECT_NAME,
                     extra_envs: dict = None):
        """
        Pulls the correct kubernetes image
        and then start the pods
        :param uuid:
        :param remove_old_installation:
        :param extra_envs:
        :param project_name:
        :return:

        """
        idparts = uuid.split('/')
        self.nuvla_uuid = idparts[1]

        add_repo_cmd = f'helm repo add {cte.NUVLAEDGE_KUBE_LOCAL_REPO_NAME} {cte.NUVLAEDGE_KUBE_REPO}'
        result: Result = self.device.run_sudo_command(add_repo_cmd, envs=_KUBECONFIG_ENV)
        if result.failed:
            self.logger.error(f'Could not add repo to helm {cte.NUVLAEDGE_KUBE_REPO}: {result.stderr}')

        update_repo_cmd = f'helm repo update nuvlaedge {cte.NUVLAEDGE_KUBE_LOCAL_REPO_NAME}'
        result: Result = self.device.run_sudo_command(update_repo_cmd, envs=_KUBECONFIG_ENV)
        if result.failed:
            self.logger.error(f'Could not update helm repo {cte.NUVLAEDGE_KUBE_LOCAL_REPO_NAME}: {result.stderr}')

        if self.deployment_branch:
            path = f'{cte.ROOT_PATH}{cte.ENGINE_PATH}deployment'
            self.device.run_sudo_command(f'sudo rm -Rf {path}', envs=_KUBECONFIG_ENV)
            self.device.run_command(cte.DEPLOYMENT_GIT_CLONE.format(branch=self.deployment_branch,
                                                                    path=path))
            chart = f'{path}/helm'
        else:
            chart = f'{cte.NUVLAEDGE_KUBE_LOCAL_REPO_NAME}/{cte.NUVLAEDGE_KUBE_LOCAL_CHART_NAME}'
            if self.nuvlaedge_version and self.nuvlaedge_version != 'latest':
                chart += f' --version={self.nuvlaedge_version}'

        install_image_cmd = cte.NUVLAEDGE_KUBE_INSTALL_IMAGE.format(
            uuid=self.nuvla_uuid,
            chart=chart,
            hostname=self.device.hostname,
            organization=self.engine_configuration.ne_image_organization,
            version=self.engine_configuration.ne_image_tag
        )
        self.project_name = project_name

        if self.include_peripherals:
            for peripheral in self.peripherals:
                cmd_arg = f' --set peripheralManager{peripheral}=true '
                install_image_cmd = install_image_cmd + cmd_arg

        envs_configuration: dict = self.engine_configuration.model_dump(by_alias=True)
        if extra_envs:
            envs_configuration.update(extra_envs)
        envs_configuration.update(_KUBECONFIG_ENV)

        self.logger.info(f'Starting NuvlaEdge with UUID: {self.nuvla_uuid} with'
                         f' configuration: '
                         f'\n\n {json.dumps(envs_configuration, indent=4)} \n')
        self.device.run_sudo_command(install_image_cmd, envs=envs_configuration)

        self.namespace = self.__get_current_nuvlaedge_namespace_running()

        if self.cred_check_thread is None:
            self.cred_check_thread = CertificateSignCheck(device_config=self.device.target_config,
                                                          uuid=self.nuvla_uuid,
                                                          namespace=self.namespace, 
                                                          logger=self.logger)
            self.cred_check_thread.start()

        self.logger.info('Device start command executed')

    def add_peripheral(self):
        pass

    def remove_peripheral(self):
        pass

    def stop_engine(self):
        if not self.namespaces_running:
            self.namespaces_running = self.__get_namespaces_running()
        for namespace in self.namespaces_running:
            if namespace.__contains__('kube') or namespace == 'default':
                continue
            deployments = self.__get_deployments_running(namespace)
            for deployment in deployments:
                stop_cmd = (f'sudo kubectl scale -n {namespace} deployment '
                            f'{deployment} --replicas=0')
                try:
                    self.device.run_sudo_command(stop_cmd, envs=_KUBECONFIG_ENV)
                except invoke.exceptions.UnexpectedExit as ex:
                    self.logger.error(f'Unexpected exit on command {stop_cmd} : Exception : {ex}')
                except Exception as ex:
                    self.logger.error(f'Error while stopping deployment {deployment}: {ex}')

    def get_authorized_keys(self):
        return self.device.run_sudo_command("sudo cat /root/.ssh/authorized_keys")

    def get_engine_logs(self):
        self.logger.info(f'Retrieving Log files from engine run with UUID: {self.engine_configuration.nuvlaedge_uuid}')
        get_pods_cmd = (f'sudo kubectl get pods -n {self.namespace} -o json | '
                        'jq \'.items[] | select(.status.phase == "Running") | .metadata.name\'')
        result: Result = self.device.run_sudo_command(get_pods_cmd, envs=_KUBECONFIG_ENV)
        if result.failed or result.stdout == '':
            return

        # 1. Get all pods in the concerned namespace
        self.logger.debug(f'Extracting logs from: \n\n\t{result.stdout}\n')
        pods = result.stdout.split('\n')

        # 2. Iteratively copy logs from kubernetes pods
        #    to /tmp/<new_folder> and chmod before transferring it to the running machine
        self.device.run_sudo_command(
            f'sudo mkdir -p /tmp/{self.engine_configuration.compose_project_name}/logs')
        local_tmp_path: Path = Path(f'/tmp/{self.engine_configuration.compose_project_name}/logs')
        local_tmp_path.mkdir(parents=True, exist_ok=True)

        # 3. Provide permissions to the folder
        self.device.run_sudo_command(
            f'sudo chmod 777 /tmp/{self.engine_configuration.compose_project_name}/logs')

        for pod in pods:
            if pod != '':
                pod = pod.replace('"', '')
                try:
                    self.get_container_logs(pod)
                except Exception as ex:
                    self.logger.warning(f'Error while downloading logs for pod {pod} : {ex}')

    def get_container_logs(self, pod, download_to_local=False, path: Path = None):
        get_logs_cmd = (f'sudo kubectl logs -n {self.namespace} {pod} >> '
                        f'/tmp/{self.engine_configuration.compose_project_name}/logs/{pod}.log')
        self.device.run_sudo_command(get_logs_cmd, envs=_KUBECONFIG_ENV)

        if download_to_local and path is not None:
            self.device.download_remote_file(remote_file_path=f'/tmp/{pod}.log',
                                             local_file_path=path / (pod + '.log'))

    def get_coe_type(self):
        return "kubernetes"

    def engine_running(self) -> bool:
        check_pods_cmd = f'sudo kubectl get pods -n {self.namespace} --no-headers'
        result: Result = None
        try:
            result = self.device.run_sudo_command(check_pods_cmd, envs=_KUBECONFIG_ENV)
            if result.failed or result.stdout.__contains__('No resources found'):
                return False
        except Exception as ex:
            self.logger.warning(f'Exception occurred {ex}')
            return False
        return True

    def finish_tasks(self):
        if self.cred_check_thread:
            self.logger.debug("Waiting for credentials check thread to close")
            self.cred_check_thread.join(50)

    def remove_engine(self, uuid: NuvlaUUID = None, black_list: list = None):
        self.logger.debug(f'Removing engine in device {self.device}')
        self.finish_tasks()

        if not self.nuvla_uuid:
            self.nuvla_uuid = uuid
        ne_id = self.nuvla_uuid.split('/')
        if len(ne_id) > 1:
            ne_id = ne_id[1]
        else:
            self.logger.warning(f"Invalid NuvlaEdge UUID {self.nuvla_uuid}")
            return

        self.namespaces_running = self.__get_namespaces_running()
        commands: list = ['sudo kubectl delete '
                          'clusterrolebindings.rbac.authorization.k8s.io '
                          'nuvla-crb '
                          f'nuvlaedge-service-account-cluster-role-binding-{ne_id}']

        for namespace in self.namespaces_running:
            if namespace.__contains__('kube') or namespace == 'default':
                continue
            commands.append(f'sudo kubectl delete ns {namespace}')
            commands.append(f'helm uninstall {namespace}')

        for cmd in commands:
            try:
                self.device.run_sudo_command(cmd, envs=_KUBECONFIG_ENV)
            except invoke.exceptions.UnexpectedExit as ex:
                self.logger.error(f'Unexpected exit on command {cmd} : Exception : {ex}')
            except Exception as ex:
                self.logger.error(f'Unable to run commands on {self.device} {ex}')

    def peripherals_running(self, peripherals: set) -> bool:
        get_all_pods_running_cmd = (f'sudo kubectl get -n {self.namespace} pods -o json | '
                                    'jq \'.items[] | select(.status.phase == "Running") | '
                                    '.metadata.name | select(contains("peripheral-manager"))\'')

        result: Result = self.device.run_sudo_command(get_all_pods_running_cmd, envs=_KUBECONFIG_ENV)
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

    def purge_engine(self, uuid: NuvlaUUID = None):
        """
            This will remove all pods and namespaces for kubernetes
        :return:
        """
        self.stop_engine()
        self.remove_engine(uuid)

    def __get_current_nuvlaedge_namespace_running(self):
        get_curr_nuvlaedge_namespace_cmd = ('sudo kubectl get namespaces -o json | jq '
                                            '\'.items[].metadata.labels."kubernetes.io/metadata.name"'
                                            f' | select(contains("{self.nuvla_uuid}"))\'')
        result: Result = self.device.run_sudo_command(get_curr_nuvlaedge_namespace_cmd, envs=_KUBECONFIG_ENV)
        namespaces = result.stdout.split('\n')
        namespace = namespaces[0].replace('"', '')
        return namespace

    def __get_namespaces_running(self) -> list:
        get_nuvla_namespaces_cmd = ('sudo kubectl get namespaces -o json | jq '
                                    '\'.items[].metadata.labels."kubernetes.io/metadata.name"\'')
        result: Result = self.device.run_sudo_command(get_nuvla_namespaces_cmd, envs=_KUBECONFIG_ENV)
        namespaces = result.stdout
        list_namespaces = namespaces.split('\n')

        output = []
        for namespace in list_namespaces:
            if namespace:
                output.append(namespace.replace('"', ''))
        running_namespaces = ' '.join([str(item) for item in output])
        self.logger.debug(f'Current namespaces running {running_namespaces}')
        return output

    def __get_deployments_running(self, namespace):
        get_deployments_cmd = (f'sudo kubectl get deployments -n {namespace} -o json | '
                               'jq \'.items[] | select(.spec.replicas != 0) | .metadata.name\'')
        result: Result = self.device.run_sudo_command(get_deployments_cmd, envs=_KUBECONFIG_ENV)
        output = []
        if result.failed or result.stdout == '':
            return output
        deployments = result.stdout
        list_deployments = deployments.split('\n')

        for deployment in list_deployments:
            if deployment:
                output.append(deployment.replace('"', ''))
        running_deployments = ' '.join([str(item) for item in output])
        self.logger.debug(f'Current deployments running {running_deployments}')
        return output


def get_pod_name(device: TargetDevice, namespace, app_name, status: str = 'Running'):
    get_pod_cmd = (f'sudo kubectl get -n {namespace} pods -o json |'
                   f' jq \'.items[] | select(.status.phase == "{status}") | '
                   f'.metadata.name | select(contains("{app_name}"))\'')
    result: Result = device.run_sudo_command(get_pod_cmd, envs=_KUBECONFIG_ENV)
    if result.failed or result.stdout == '':
        return ''
    list_names = result.stdout.strip().split('\n')
    return list_names[0].replace('"', '')


def get_environmental_value(device, namespace, pod_name, key, logger):
    get_pod_details = f'sudo kubectl get pod -n {namespace} {pod_name} -o json'
    result: Result = device.run_sudo_command(get_pod_details, envs=_KUBECONFIG_ENV)
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
    
    def __init__(self, device_config: TargetDeviceConfig, uuid, namespace, logger: logging.Logger):
        super(CertificateSignCheck, self).__init__()
        self.device = SSHTarget(device_config)
        self.exit_event: Event = Event()
        self.namespace = namespace
        self.logger = logger
        self.uuid = uuid

    def join(self, timeout: float | None = 0):
        self.logger.debug('Exiting Certificate sign check thread')
        self.exit_event.set()
        super(CertificateSignCheck, self).join(timeout)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(f'{self.__class__.__name__}: {msg}', *args, **kwargs)

    def run(self):
        credentials_pod = ''
        while credentials_pod == '':
            credentials_pod = get_pod_name(self.device, self.namespace, cte.NUVLAEDGE_KUBE_CERTIFICATE_MANAGER)
            time.sleep(0.5)

        csr_name = get_environmental_value(self.device, self.namespace, credentials_pod,
                                           cte.NUVLAEDGE_KUBE_CSR_NAME_KEY, self.logger)

        if csr_name == 'nuvlaedge-csr':
            csr_name += '-' + self.uuid

        time_to_sleep = 2
        while not self.exit_event.is_set():
            get_csr_cmd = (f'sudo kubectl get certificatesigningrequests.certificates.k8s.io -o json | jq \'.items[] | '
                           f'select(.metadata.name == "{csr_name}") | '
                           '.status.conditions[0].type\'')

            self.exit_event.wait(time_to_sleep)

            if not self.device.is_reachable():
                self.debug('Device not reachable.')
                continue

            result: Result = self.device.run_sudo_command(get_csr_cmd, envs=_KUBECONFIG_ENV)
            if result.failed:
                self.debug(f'Running following command failed: {get_csr_cmd}')
                continue

            status = result.stdout
            status = status.strip().replace('"', '')
            if status == "Approved":
                time_to_sleep = 50
                self.debug('Certificate is approved')
                continue

            # approve certificate
            approve_csr_cmd = f'sudo kubectl certificate approve {csr_name}'
            try:
                self.device.run_sudo_command(approve_csr_cmd, envs=_KUBECONFIG_ENV)
            except Exception as ex:
                self.logger.warning(f'Approval of csr command failed : {ex}')
            self.logger.info(f'Approved certificate {csr_name}')
