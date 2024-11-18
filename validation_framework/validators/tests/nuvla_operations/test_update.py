import concurrent.futures
import json
import logging
import re
import threading
import time
from dataclasses import dataclass
from datetime import datetime

import requests

from nuvla.api import Api as NuvlaClient
from nuvla.api.models import CimiResource, CimiResponse
from packaging.version import Version
from pydantic import BaseModel, ConfigDict

from validation_framework.common.constants import DEFAULT_JOBS_TIMEOUT
from validation_framework.common.nuvla_uuid import NuvlaUUID
from validation_framework.deployer.engine_handler import EngineHandler
from validation_framework.common import constants as cte, constants
from validation_framework.validators.tests.nuvla_operations import validator
from validation_framework.validators import ValidationBase

"""
Test engine update

This validation tests will always try to update from the latest's releases to the current target 
version (Most likely in NuvlaDev)
"""

GH_API_URL = "https://api.github.com/repos/{repo}/releases"
NUVLA_RELEASE_ENDPOINT = "https://nuvla.io/api/nuvlabox-release"
MINIMUM_K8S_VERSION = "2.18.0"

@dataclass
class FutureResult:
    origin: str
    target: str
    msg: str
    was_successful: bool

@validator('UpdateNuvlaEdge')
class UpdateNuvlaEdge(ValidationBase):
    release_id: str
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.engines: dict[str, EngineHandler] = {}
        self.uuids: dict[str, str] = {}
        self.is_skip: bool = False

    def run_update(self, origin, target):
        self.logger.info(f"Starting update from {origin}(Minimum {MINIMUM_K8S_VERSION}) to {target}")
        self.logger.info("Engine keys are: " + str(self.engines.keys()))
        self.custom_setup(origin, target)
        engine = self.engines[origin]

        if Version(origin) < Version(MINIMUM_K8S_VERSION) and engine.coe_type == 'kubernetes':
            self.logger.info(f"Skipping {origin} to {target} update. Minimum NuvlaEdge version for Kubernetes validation update is {MINIMUM_K8S_VERSION}")
            self.is_skip = True
            self.skipTest("Minimum NuvlaEdge version for Kubernetes validation update is not met")

        uuid = self.uuids[origin]

        self.wait_for_commissioned(engine=engine, uuid=NuvlaUUID(uuid))
        self.logger.info(f"Updating {engine.device_config.alias}-{uuid} from {origin} to {target}")

        self.logger.info(f"Waiting for remote version on {uuid}")
        version, params = self.wait_update_ready(uuid=NuvlaUUID(uuid))
        self.logger.info(f"Remote version is {version}")
        self.assertNotEqual(version, "UNKNOWN", "Remote version is unknown, cannot proceed")
        self.assertNotEqual(params, "UNKNOWN", "Installation params are unknown, cannot proceed")
        self.assertEqual(version, origin, "Remote version is not the expected one")


        update_payload = self._build_payload(engine, target, origin, uuid, params)
        assert type(update_payload) == dict

        self.logger.info(f"Updating with payload {json.dumps(update_payload, indent=4)}")
        nuvlabox: CimiResource = self.nuvla_client.get(uuid)
        resp: CimiResponse = self.nuvla_client.operation(nuvlabox, 'update-nuvlabox', data=update_payload)

        self.logger.info(f"Update operation started:\n{json.dumps(resp.data, indent=4)}")
        job_id = resp.data.get('location')
        final_state = self.wait_job_success(job_id)
        self.assertEqual(final_state, "SUCCESS", f"Job {job_id} did not reach SUCCESS ({final_state}) state in time {DEFAULT_JOBS_TIMEOUT}")

        ## Gather online history of the NuvlaEdge and assert an online percentage
        online: list[bool] = self.gather_online_data(300, uuid)

        self.assertTrue(online.count(True) > 0.8 * len(online), "NuvlaEdge was not online most of the time, something went wrong")

        status_id = self.nuvla_client.get(uuid).data['nuvlabox-status']
        final_version = self.nuvla_client.get(status_id, select=["nuvlabox-engine-version"]).data['nuvlabox-engine-version']
        self.assertEqual(final_version, target, f"Final version is not the expected one {target}")

        # Here to allow tear down of ValidationBase to run without issues
        self.uuid = NuvlaUUID(uuid)
        self.engine_handler = engine

    def gather_nuvla_version(self, timeout: int, uuid: str) -> list[str]:
        status_id = self.nuvla_client.get(uuid).data['nuvlabox-status']
        start_time: float = time.time()

        while time.time() - start_time < timeout:
            status = self.nuvla_client.get(status_id, select=["nuvlabox-engine-version"])
            if status.data['status'] == 'UNKNOWN':
                time.sleep(3)
            else:
                return status.data['status']

    def gather_online_data(self, timeout: int, uuid: str) -> list[bool]:
        online: list[bool] = []
        start_time: float = time.time()


        while time.time() - start_time < timeout:
            nb = self.nuvla_client.get(uuid, select=["online"])
            online.append(nb.data.get('online', False))
            time.sleep(3)

        return online


    def wait_job_success(self, job_id: str) -> str:
        start_time: float = time.time()
        self.logger.info(f'Waiting {DEFAULT_JOBS_TIMEOUT} seconds for job {job_id} to reach SUCCESS state')
        job_state = "UNKNOWN"
        while job_state != "SUCCESS":
            if time.time() - start_time > DEFAULT_JOBS_TIMEOUT:
                self.logger.error("Job not completed in time")
                return job_state

            time.sleep(3)
            job_state = self.nuvla_client.get(job_id, select=["state"]).data.get("state", "UNKNOWN")

        return job_state

    @staticmethod
    def _get_installation_parameters(params: dict) -> dict:
        params["environment"] = {k.split("=")[0]: k.split("=")[1]  for k in params["environment"] if "=" in k}
        return params

    def _build_payload(self, engine: EngineHandler, target_image: str, origin_version: str, uuid: str, params: dict) -> dict:
        self.logger.info(f"Building payload for update from {origin_version} to {target_image}")
        params: dict = self._get_installation_parameters(params)
        d = params['environment']
        self._set_image_env(engine, target_image, d)

        payload = UpdatePayload(
            project_name=params['project-name'],
            environment=[f"{k}={v}" for k, v in d.items()],
            current_version=origin_version,
            force_restart=False,
            working_dir=params.get('working-dir', ""),
            config_files=["docker-compose.yml"]
        )

        return UpdateData(
            nuvlabox_release=self.release_id,
            payload=payload.model_dump_json(by_alias=True)
        ).model_dump(by_alias=True)

    @staticmethod
    def _set_image_env(engine: EngineHandler, image: str, envs: dict[str, str]):
        if engine.coe_type == 'docker':
            envs['NE_IMAGE_TAG'] = image
            envs['NE_IMAGE_ORGANIZATION'] = 'nuvladev'
        elif engine.coe_type == 'kubernetes':
            envs['nuvlaedge.image.image'] = image
            envs['nuvlaedge.image.organization'] = 'nuvladev'
        else:
            raise ValueError(f"Unknown COE type {engine.coe_type}")

    @staticmethod
    def get_sorted_releases():
        nuvla_releases = requests.get(NUVLA_RELEASE_ENDPOINT).json()["resources"]
        pattern = re.compile(r'^\d+\.\d+\.\d+$')

        def get_latest(pat, releases, ind = -1):
            if releases[ind]['published'] and pattern.match(releases[ind]['release']):
                return releases[ind]['id']
            else:
                if ind*-1 == len(releases):
                    return ""
                return get_latest(pat, releases, ind - 1)

        sorted_releases = sorted(nuvla_releases,
                                 key=lambda x: datetime.strptime(x['release-date'], '%Y-%m-%dT%H:%M:%SZ'))

        latest_release_id = get_latest(pattern, sorted_releases)
        return [(r['release'], latest_release_id if latest_release_id else r['id']) for r in nuvla_releases if r['published'] and pattern.match(r['release'])]

    def custom_setup(self, origin_version, target_version):

        self.engines[origin_version] = EngineHandler(
            cte.DEVICE_CONFIG_PATH / self.target_config_file,
            nuvlaedge_version=origin_version,
        )

        self.uuids[origin_version] = self.create_nuvlaedge_in_nuvla(
            suffix=f"-update-{origin_version}-to-{target_version}")

    def setUp(self) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)

        self.nuvla_client: NuvlaClient = NuvlaClient(reauthenticate=True)
        self.nuvla_client.login_apikey(self.nuvla_api_key, self.nuvla_api_secret)

    def tearDown(self) -> None:
        if not self.is_skip:
            super().tearDown()

def underscore_to_hyphen(field_name: str) -> str:
    """
    Alias generator that takes the field name and converts the underscore into hyphen
    Args:
        field_name: string that contains the name of the field to be processed

    Returns: the alias name with no underscores

    """
    return field_name.replace("_", "-")

class CustomBase(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=underscore_to_hyphen,
        validate_assignment=True
    )

class UpdatePayload(CustomBase):
    project_name: str
    working_dir: str
    environment: list[str]
    force_restart: bool
    current_version: str
    config_files: list[str]


class UpdateData(CustomBase):
    nuvlabox_release: str
    payload: str
