"""
Higher class that wraps together the device and the release handler
"""
import logging
from pathlib import Path

from common import Release
from common import utils
from common.nuvla_uuid import NuvlaUUID
from common.schemas.release import TargetReleaseConfig
from common.schemas.target_device import TargetDeviceConfig
from common import  constants as cte
from deployer import SSHTarget
from deployer.release_handler import ReleaseHandler


class EngineHandler:
    """
    (NuvlaEdge)
    """
    # TODO: Move this variable to proper place
    target_dir: str = ''
    nuvlaedge_uuid: NuvlaUUID = ''

    def __init__(self, target_device: int | Path, target_release: str):
        """
        Engine handler constructor. It is in charge of assessing if the targets are passed as index or path to file.
        If an index is passed has to find the corresponding file in the default folder, if it's a path, directly
        loads the configuration.
        :param target_device: Index or path to target device file
        :param target_release: Index or Release tag or path to target release file
        """
        self.logger: logging.Logger = logging.getLogger(__name__)

        # Assess device configuration
        if isinstance(target_device, int):
            self.logger.error('Gather information from index')
            self.device_config_file: Path = Path(self.get_device_config_by_index(target_device))
        else:
            self.logger.error('Gather information from path')
            self.device_config_file: Path = target_device
        if not self.device_config_file.is_file():
            raise FileNotFoundError(f'Provided file {self.device_config_file} does not exists')

        self.device_config: TargetDeviceConfig = utils.get_model_from_toml(TargetDeviceConfig, self.device_config_file)
        self.device: SSHTarget = SSHTarget(self.device_config)

        # Asses release configuration
        try:
            self.release_config: TargetReleaseConfig = TargetReleaseConfig(tag=Release(target_release))
            self.release_handler: ReleaseHandler = ReleaseHandler(self.release_config, std_release=True)
            self.logger.error(f'Gather information from release {self.release_config}')
        except ValueError:
            self.logger.error('Gather information from path')
            self.release_config: TargetReleaseConfig = utils.get_model_from_toml(TargetReleaseConfig,
                                                                                 Path(target_release))
            self.release_handler: ReleaseHandler = ReleaseHandler(self.release_config, std_release=False)

    @staticmethod
    def get_device_config_by_index(device_index: int) -> Path:
        """

        :param device_index: Numerical index to identify specific device configurations
        :return: The file location
        """
        for file in cte.DEVICE_CONFIG_PATH.iterdir():
            if file.is_file() and file.name.startswith(str(device_index)):
                return cte.DEVICE_CONFIG_PATH / file

        raise IndexError(f'Device with index {device_index} not found in {cte.DEVICE_CONFIG_PATH}')

    def prepare_compose_files(self):
        """

        :return: the path location of the files.
        """
        self.target_dir: str = cte.ROOT_PATH + cte.ENGINE_PATH + self.release_handler.release_tag
        self.logger.error(f'Downloading files for release {self.release_handler.release_tag} into {self.target_dir}/')
        self.device.run_command(f'mkdir -p {cte.ROOT_PATH + cte.ENGINE_PATH}/{self.release_handler.release_tag}')
        for link in self.release_handler.get_download_cmd():
            self.device.download_file(link=link,
                                      file_name=link.split('/')[-1],
                                      directory=self.target_dir)

    def start_engine(self, nuvlaedge_uuid: NuvlaUUID, remove_old_installation: bool = False):
        """

        :return:
        """
        if remove_old_installation:
            # 1. - Clean target
            self.device.clean_target()

        # 2. - Check remote files
        self.prepare_compose_files()

        # 3. - Start engine with target release (Future custom as well)
        files: str = f' -f '.join([self.target_dir+'/'+i for i in self.release_handler.requested_release.components])
        print(files)
        start_command: str = cte.COMPOSE_UP.format(prepend='nohup',
                                                   project_name=cte.PROJECT_NAME,
                                                   files=files)
        print(start_command)
        envs_configuration: dict = {'NUVLABOX_UUID': nuvlaedge_uuid}
        # self.release_handler.build_envs_configuration()
        self.logger.info(f'Starting engine with Edge uuid: {nuvlaedge_uuid}')

        self.device.run_command(start_command, envs=envs_configuration)
        self.logger.info('Device started')

    def stop_engine(self) -> bool:
        """

        :return:
        """
        if not self.engine_running():
            self.logger.info('Engine not running')
            return True

        self.device.clean_target()
        if self.engine_running():
            return False

    def engine_running(self) -> bool:
        """

        :return:
        """
        self.device.run_command('docker ps')
        return True

    def clean_device(self):
        """

        :return:
        """


