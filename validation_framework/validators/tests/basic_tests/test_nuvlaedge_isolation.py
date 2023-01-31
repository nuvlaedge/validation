"""
Tests the capability of NuvlaEdge to run in parallel. Isolation is only available for versions 2.6.0 onwards
"""
import time

import invoke

from validation_framework.validators import ValidationBase
from validation_framework.validators.tests.basic_tests import validator


# @validator('NuvlaEdgeIsolation')
class TestNuvlaEdgeIsolation(ValidationBase):
    def test_nuvlaedge_isolation(self):
        self.wait_for_commissioned()
        self.wait_for_operational()

        self.logger.info('')