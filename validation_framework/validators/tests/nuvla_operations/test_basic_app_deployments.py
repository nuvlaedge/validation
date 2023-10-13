"""

"""
import time
import unittest

from nuvla.api.resources import Deployment

from validation_framework.validators import ValidationBase
from validation_framework.validators.tests.nuvla_operations import validator
from validation_framework.common.constants import DEFAULT_DEPLOYMENTS_TIMEOUT
from nuvla.api.models import CimiResponse, CimiResource, CimiCollection


#@validator('BasicAppDeployment')
class TestBasicAppDeployment(ValidationBase):
    APP_NAME: str = 'Nginx App in Kubernetes'
    MODULE_ID: str = 'module/95e17c68-11e5-482e-b887-b34b1a322e7d'

    STATE_PENDING: str = 'PENDING'
    STATE_STARTED: str = 'STARTED'
    STATE_STOPPING: str = 'STOPPING'
    STATE_STOPPED: str = 'STOPPED'
    STATE_ERROR: str = 'ERROR'

    def get_app_data(self):
        """
        Retrieves and prepares the data structure for the application to be deployed.
        :return: App data structure
        """

    def wait_for_deployment_start(self, deployment_id):
        state: str = self.nuvla_client.get(deployment_id).data.get('state')
        self.logger.info(f'Waiting for deployment {deployment_id} to start')
        start_time: float = time.time()
        while state != self.STATE_STARTED:
            time.sleep(1)
            state = self.nuvla_client.get(deployment_id).data.get('state')

            if time.time() > start_time + DEFAULT_DEPLOYMENTS_TIMEOUT or state == self.STATE_ERROR:
                self.logger.error(f'Deployment {deployment_id} did not start in time. State {state}')
                self.assertTrue(False, f'Deployment {deployment_id} did not start in time')

        self.logger.info('Deployment Started')

    def stop_deployment(self, deployment_id):
        deployment_resource: Deployment = Deployment(self.nuvla_client)
        deployment_resource.stop(deployment_id)

        state: str = self.nuvla_client.get(deployment_id).data.get('state')

        self.logger.info(f'Waiting for deployment {deployment_id} to stop')
        start_time: float = time.time()
        while state != self.STATE_STOPPED:
            time.sleep(1)
            state = self.nuvla_client.get(deployment_id).data.get('state')

            if time.time() > start_time + DEFAULT_DEPLOYMENTS_TIMEOUT:
                self.logger.error(f'Deployment {deployment_id} did not stop in time. Cannot remove remaining ')
                return

        self.logger.info(f'Trying to remove {deployment_id}')
        deployment_resource.delete(deployment_id)

    def configure_deployment(self, pull=False) -> str:
        """

        :param pull:
        :return:
        """

        nuvlabox_res: CimiResource = self.nuvla_client.get(self.uuid)
        nuvlabox_data: dict = nuvlabox_res.data
        nuvlabox_isg_id: str = nuvlabox_data['infrastructure-service-group']
        nuvlabox_isg: dict = self.nuvla_client.get(nuvlabox_isg_id).data
        nuvlabox_is_id = nuvlabox_isg['infrastructure-services'][0]['href']

        # Find credential
        # Credentials finding
        filter = f"method^='infrastructure-service-' and parent='{nuvlabox_is_id}'"
        resp: CimiCollection = self.nuvla_client.search("credential", filter=filter)
        infra_cred: str = resp.resources[0].id

        new_dep = Deployment(self.nuvla_client)
        coe_type = self.engine_handler.get_coe_type()

        if coe_type == 'docker':
            self.MODULE_ID = 'module/96f09292-6aa4-49e1-a5d6-e0fb90fbf787'

        deploy_res: CimiResource = new_dep.create(self.MODULE_ID, infra_cred_id=infra_cred)
        deploy_data: dict = deploy_res.data

        if pull:
            deploy_data['execution-mode'] = 'pull'
            self.nuvla_client.edit(deploy_data.get('id'), deploy_data)
        else:
            deploy_data['execution-mode'] = 'push'
            self.nuvla_client.edit(deploy_data.get('id'), deploy_data)

        return deploy_data.get('id')


    def test_app_deployment_pull(self):
        self.logger.info(f'Starting pull application deployment validation tests')
        self.wait_for_commissioned()
        self.wait_for_operational()
        self.logger.info('Wait a long time to let everything set up')
        time.sleep(120)
        self.logger.info(f'Device up and ready. Launching ')
        deployment_id = self.configure_deployment(pull=True)

        self.logger.info(f"Starting deployment {deployment_id}")
        deployment_resource: Deployment = Deployment(self.nuvla_client)
        deployment_resource.start(deployment_id)

        self.wait_for_deployment_start(deployment_id)
        self.assertEqual(self.nuvla_client.get(deployment_id).data.get('state'),
                         self.STATE_STARTED,
                         f'Deployment successfully started in PULL mode')
        self.logger.info(f'Running deployment for 100 seconds')
        time.sleep(100)
        self.logger.info(f'Stopping deployment')
        self.stop_deployment(deployment_id)

    def test_app_deployment_push(self):
        if self.engine_handler.get_coe_type() == 'kubernetes':
            self.logger.info('Disabling push app deployment test for kubernetes')
            return
        self.logger.info(f'Starting push application deployment validation tests')
        self.wait_for_commissioned()
        self.wait_for_operational()
        self.logger.info('Wait a long time to let everything set up')
        time.sleep(120)
        self.logger.info(f'Device up and ready. Launching ')
        deployment_id = self.configure_deployment()

        self.logger.info(f"Starting deployment {deployment_id}")
        deployment_resource: Deployment = Deployment(self.nuvla_client)
        deployment_resource.start(deployment_id)

        self.wait_for_deployment_start(deployment_id)
        self.assertEqual(self.nuvla_client.get(deployment_id).data.get('state'),
                         self.STATE_STARTED,
                         f'Deployment successfully started in PUSH mode')
        self.logger.info(f'Running deployment for 100 seconds')
        time.sleep(100)
        self.logger.info(f'Stopping deployment')
        self.stop_deployment(deployment_id)
