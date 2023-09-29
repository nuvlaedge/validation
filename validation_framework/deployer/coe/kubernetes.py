import logging

from validation_framework.deployer.coe import COEBase
from validation_framework.deployer.target_device.target import TargetDevice


logger: logging.Logger = logging.getLogger(__name__)


class KubernetesCOE(COEBase):

    def __init__(self, device: TargetDevice):
        super().__init__(device, logger)

    def start_engine(self):
        pass

    def add_peripheral(self):
        pass

    def remove_peripheral(self):
        pass

    def stop_engine(self):
        pass

    def get_engine_logs(self):
        pass

    def get_container_logs(self, container):
        pass

    def engine_running(self):
        pass

    def remove_engine(self):
        pass

    def purge_engine(self):
        pass