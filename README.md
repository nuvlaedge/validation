# NuvlaEdge engine validation

This repository contains the source code for the NuvlaEdge validation service. A program that executes tests over a
given version/release of NuvlaEdge. The tests are performed automatically triggered by GH actions on SixSq 
custom runner.

---

# Currently implemented tests

### NuvlaEdge functional tests
| Index |                  Name | Description                                                                                                               |
|:-----:|----------------------:|---------------------------------------------------------------------------------------------------------------------------|
|   1   |   Standard Engine Run | Tests that the standard execution of the NuvlaEdge is performed as expected.                                              |
|   2   |        Device restart | Tests the resilience of the NuvlaEdge after an unexpected restart of the device                                           |  
|   3   |     Connectivity Loss | Tests the resilience of the NuvlaEdge after losing connectivity for 5 minutes                                             | 
|   4   | Container Reliability | Tests that the containers are not restarted during normal initialization. They shouldn't                                  |


### Nuvla Operations Tests
| Index | Name            | Description                                                                                                                     |
|-------|-----------------|---------------------------------------------------------------------------------------------------------------------------------|
| 1     | Reboot          | Tests the correct performance of the NuvlaEdge under the Nuvla command reboot and its proper recovery afterwards                |
| 2     | App deployment  | Using a sample application, it tests that the system is capable of working in push and pull mode when deploying and App         |
| 2     | Update          | Follows the update action and the correct result of it                                                                          |
| 3     | SSH Management  | Nuvla provides the possibility of adding and removing SSH keys in the device. This test, performs the validation on that action |



---

## Validation framework usage
The goal of this service is to provide a functional test utility for developers so both NuvlaEdge releases and new implemented features are automatically validated.

The system is automatized via GH actions integrated in all NuvlaEdge repos, including deployment which is the release controller.

To add tests to this framework there are some considerations to take into account:
1. Tests are based on python unitTest standard library and TestCase class. 
2. Tests are executed per module (e.g. basic, features, nuvla_operations, etc)
3. New validation tests must be places in a new file, named with test_* as prefix. The test class must extend the class ValidatorBase and be decorated with @validator('name_of_the_test') so the automatic system can find it. See any of the previously implemented test for reference.
4. Every TestCase must contain one single test_* method as they are intended to test a single specific functionally. However, if the testing target requires it, multiple operations can be performed.


## Validation integration with GH CI actions
This service is developed in order to be used within a organization scope. The organization should contain the validation repository.

The workflow action of this repository is in charge of updating the software in the runner everytime there is a new push into main. 

Then, trigger the validation tests the required container will have to contain a job inside its GitHub workflow as follows:
