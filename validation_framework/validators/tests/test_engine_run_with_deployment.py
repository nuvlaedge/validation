"""

"""

from validators.validation_base import ValidationBase
from validators.tests import validator


@validator('2_Run_with_deployment')
class TestRunWithDeployment(ValidationBase):
    TEST_RUN_TIME: float = 60*2.0


