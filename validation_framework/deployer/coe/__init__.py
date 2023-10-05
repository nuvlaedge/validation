import logging

from validation_framework.common.schemas.target_device import TargetDeviceConfig
from validation_framework.deployer.coe.coe_base import COEBase
from validation_framework.deployer.coe.docker import DockerCOE
from validation_framework.deployer.coe.kubernetes import KubernetesCOE


logger: logging.Logger = logging.getLogger(__name__)


def coe_factory(device_configuration: TargetDeviceConfig, **kwargs):
    match device_configuration.coe:
        case 'docker':
            return DockerCOE(device_configuration, **kwargs)

        case 'kubernetes':
            return KubernetesCOE(**kwargs)

        case _:
            logger.info(f'COE {device_configuration.coe} not implemented')
            raise NotImplementedError(f'COE {device_configuration.coe} not supported '
                                      f'by validation')
