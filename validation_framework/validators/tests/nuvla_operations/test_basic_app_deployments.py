"""

"""
from validation_framework.validators import ValidationBase


# @validator('BasicAppDeployment')
class TestBasicAppDeployment(ValidationBase):

    def get_app_data(self):
        ...

    def start_deployment(self):
        ...

    def stop_deployment(self):
        ...

    def setUp(self) -> None:
        self.engine_handler.start_engine(self.uuid, remove_old_installation=True)

    def test_app_deployment(self):
        ...
