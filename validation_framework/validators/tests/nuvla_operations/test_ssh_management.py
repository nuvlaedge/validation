"""

"""
import time
from pprint import pprint as pp
from nuvla.api.models import CimiResource, CimiResponse, CimiCollection

from validation_framework.validators.tests.nuvla_operations import validator
from validation_framework.common.constants import DEFAULT_JOBS_TIMEOUT
from validation_framework.validators import ValidationBase


@validator('SSHKeysManagement')
class TestSSHKeyManagement(ValidationBase):
    VALIDATION_SSH_ID: str = "credential/41f3180e-dcee-434a-a3f8-88e7520245f8"

    def manipulate_ssh_key(self, operation: str = 'add-ssh-key') -> bool:
        """
        Instructs nuvla to add an SSH key to the NuvlaEdge

        returns: true if successfully added (From Nuvla Job perspective). False otherwise
        """
        nuvlabox: CimiResource = self.nuvla_client.get(self.uuid)
        self.logger.debug(f"Running {operation} operation into {nuvlabox.data.get('name')}")

        payload = {
            "credential": self.VALIDATION_SSH_ID
        }
        res: CimiResponse = self.nuvla_client.operation(nuvlabox,
                                                        operation,
                                                        data=payload)
        self.logger.info(f'Received operation status {res.data.get("status")}')
        if res.data.get('status') != 202:
            self.logger.error(f"Status {res.data.get('status')} does not match success "
                              f"status 202")
            return False
        job_id: str = res.data.get('location')
        job_resource: CimiResource = self.nuvla_client.get(job_id)
        start_time: float = time.time()
        self.logger.info(f'Waiting {DEFAULT_JOBS_TIMEOUT} seconds for job {job_id} to reach SUCCESS state')
        while job_resource.data.get('state') != "SUCCESS":
            time.sleep(3)
            if time.time() - start_time > DEFAULT_JOBS_TIMEOUT:
                self.logger.error("Job not completed in time")
                return False

            job_resource = self.nuvla_client.get(job_id)
        self.logger.info(f'Job successfully ran in Nuvla')
        return True

    def is_ssh_key_present(self) -> bool:
        """
        Reads the authorized keys in the target device and checks whether the ssh is
        present or not
        returns: True if KeyText is present in authorized keys
        """
        self.logger.info(f'Gathering remote authorized keys')
        command = self.engine_handler.device.run_command("cat ~/.ssh/authorized_keys")
        return "TestPublicKey" in command.stdout

    def test_ssh_key_management(self):
        self.logger.info("Starting SSH key management validation tests")
        self.wait_for_commissioned()
        self.wait_for_operational()

        self.logger.info(f'Starting ssh management tests when status '
                         f'{self.get_nuvlaedge_status()[1]}')
        deploy_ssh_result: bool = self.manipulate_ssh_key()
        self.assertTrue(deploy_ssh_result, "SSH not properly added from Nuvla "
                                           "perspective")

        self.assertTrue(self.is_ssh_key_present(),
                        "Key not present in authorized keys ssh file")

        time.sleep(3)
        remove_ssh_result: bool = self.manipulate_ssh_key(operation='revoke-ssh-key')
        self.assertTrue(remove_ssh_result, "SSH not properly removed from Nuvla "
                                           "perspective")

        self.assertFalse(self.is_ssh_key_present(),
                         "Key should be present in authorized keys ssh file")


