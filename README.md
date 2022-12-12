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
|   2   |        App deployment | Using a sample application, it tests that the system is capable of working in push and pull mode when deploying and App   |
|   3   |        Device restart | Tests the resilience of the NuvlaEdge after an unexpected restart of the device                                           |  
|   4   |     Connectivity Loss | Tests the resilience of the NuvlaEdge after losing connectivity for 5 minutes                                             | 
|   5   | Container Reliability | Tests that the containers are not restarted during normal initialization. They shouldn't                                  |
|   6   |      VPN Connectivity | Check the VPN service is up un running. Gives a run period of 5 minutes before asserting false. If true, finishes earlier |


### Nuvla Operations Tests
| Index | Name            | Description                                                                                                                     |
|-------|-----------------|---------------------------------------------------------------------------------------------------------------------------------|
| 1     | Reboot          | Tests the correct performance of the NuvlaEdge under the Nuvla command reboot and its proper recovery afterwards                |
| 2     | Update          | Follows the update action and the correct result of it                                                                          |
| 3     | SSH Management  | Nuvla provides the possibility of adding and removing SSH keys in the device. This test, performs the validation on that action |
| 4     | Cluster Manager | Assess the correct functionality of the clustering action in when the node is set as manager                                    |
| 5     | Cluster         | Assess the correct functionality of the clustering action in when the node is set as worker                                     |                                                                                                                            |



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


Sample template:
```yaml
name: "<REPO_NAME>Validation"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref_name }}
  cancel-in-progress: true

on:
  push:
    branches:
      - "main"
    pull_request:
  workflow_dispatch:

env:
  VALIDATION_PACKAGE_NAME: "validation-latest-py3-none-any.whl"

jobs:
  validate-release:
    strategy:
      matrix:
        board-config: [ "rpi4", "ubuntu_vm" ]
        validation-type: [ "basic_tests", "nuvla_operations" ]
    runs-on: ${{ matrix.board-config }}

    steps:
      - name: CheckOut validation packages
        run: |
          curl -u "${{ secrets.VALIDATION_TOKEN_USERNAME }}:${{ secrets.VALIDATION_TOKEN_SECRET }}" \
          -H 'Accept: application/vnd.github.v3.raw' \
          -O --create-dirs --output-dir conf/targets/ \
          -L "https://api.github.com/repos/nuvlaedge/validation/contents/conf/targets/${{ matrix.board-config }}.toml" \
          

      - name: Gather System configuration
        run: |
          curl -u "${{ secrets.VALIDATION_TOKEN_USERNAME }}:${{ secrets.VALIDATION_TOKEN_SECRET }}" \
          -H 'Accept: application/vnd.github.v3.raw' \
          -O -L "https://api.github.com/repos/nuvlaedge/validation/contents/${{ env.VALIDATION_PACKAGE_NAME }}"

      - name: Setup Python environment
        uses: actions/setup-python@v4
        with:
          python-version: '3.10.8'

      - name: Install Validation Framework dependency
        run: pip install ${{ env.VALIDATION_PACKAGE_NAME }}  --force-reinstall

      - name: Setup results folder
        run: |
          mkdir -p temp_results/xml temp_results/json

      # FUTURE: Store results somewhere else?
      - name: Clear previous results
        run: |
          rm temp_results/xml/*.xml

      - name: Run Validation on board ${{ matrix.board-config }}
        run: |
          python -m validation_framework --target ${{ matrix.board-config }}.toml \
          --validator ${{ matrix.validation-type }} --microservice ${{ github.event.repository.name }}

      - name: Publish Unit Test Results
        uses: EnricoMi/publish-unit-test-result-action/composite@v2
        if: always()
        with:
          junit_files: "results/xml/*.xml"
```
