"""

"""
import logging
from typing import NoReturn
import time

from nuvla.api import Api
from nuvla.api.models import CimiResponse

from common.nuvla_uuid import NuvlaUUID
from common.schemas.edge_schema import EdgeSchema
from common.schemas.user_schema import (UserSchema)
from common.release import Release


class NuvlaIO:
    def __init__(self, endpoint: str):
        """

        """
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)

        # Nuvla API instance
        self.nuvla_client: Api = Api(endpoint=endpoint, persist_cookie=False)

        # UserInfo
        self.user_info: UserSchema = UserSchema()

    def log_to_nuvla(self, key: str, secret: str, config_file: str) -> NoReturn:
        """
        Logs in to nuvla using the api keys and secret provided via env. variables
        :return: None
        """
        if self.user_info.API_KEY and self.user_info.API_SECRET:
            print('Logging to Nuvla with environmental variables')
            self.nuvla_client.login_apikey(self.user_info.API_KEY,
                                           self.user_info.API_SECRET)

    def create_edge(self, version: Release, name: str = '[Validation] Test {}') -> NuvlaUUID:
        """
        Creates a new Edge in to the provided
        :param version: Version being deployed
        :param name: Name to be assigned to the new Edge
        :return: The UUID of the successfully created Edge, empty string otrherwise
        """

        self.logger.debug(f'Creating remove validation edge')

        it_edge_conf: EdgeSchema = EdgeSchema(name=name)

        # Version corresponds to the first digit of the release
        it_edge_conf.version = int(it_edge_conf.release.split('.')[0])

        response: CimiResponse = self.nuvla_client.add('nuvlabox',
                                                       data=it_edge_conf.dict(exclude={'uuid'}, by_alias=True))
        it_edge_conf.uuid = response.data.get('resource-id')
        return it_edge_conf.uuid

    def remove_edge(self, nuvlaedge_uuid: NuvlaUUID) -> bool:
        """
        Removes the remote created Edge
        :param nuvlaedge_uuid: UUID of the edge to be removed
        :return: True if  successfully removed, false otherwise
        """
        ne_state: str = self.nuvla_client.search('nuvlabox',
                                                 filter=f'id=="{nuvlaedge_uuid}"').resources[0].data['state']

        if ne_state in ['COMMISSIONED']:
            self.nuvla_client.get(nuvlaedge_uuid + "/decommission")

        while ne_state not in ['DECOMMISSIONED', 'NEW']:
            time.sleep(1)
            ne_state = self.nuvla_client.search(
                'nuvlabox', filter=f'id=="{nuvlaedge_uuid}"').resources[0].data['state']

