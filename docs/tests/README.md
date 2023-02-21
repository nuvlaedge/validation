# Tests

For the list of the tests see

* [Basic Tests](01%20Basic%20Tests.md)
* [Nuvla Operations](02%20Nuvla%20Operations.md)

## NuvlaEdge functional tests

| Index |                  Name | Description                                                                                                               |
|:---:|----------------------:|---------------------------------------------------------------------------------------------------------------------------|
|1   |   Standard Engine Run | Tests that the standard execution of the NuvlaEdge is performed as expected.                                              |
|2   |        Device restart | Tests the resilience of the NuvlaEdge after an unexpected restart of the device                                           |  
|3   |     Connectivity Loss | Tests the resilience of the NuvlaEdge after losing connectivity for 5 minutes                                             | 
|4   | Container Reliability | Tests that the containers are not restarted during normal initialization. They shouldn't                                  |


## Nuvla operations tests

| Index | Name            | Description                                                                                                                     |
|:---:|-----------------|---------------------------------------------------------------------------------------------------------------------------------|
| 1   | Reboot          | Tests the correct performance of the NuvlaEdge under the Nuvla command reboot and its proper recovery afterwards                |
| 2   | App deployment  | Using a sample application, it tests that the system is capable of working in push and pull mode when deploying and App         |
| 3   | Update          | Follows the update action and the correct result of it                                                                          |
| 4   | SSH Management  | Nuvla provides the possibility of adding and removing SSH keys in the device. This test, performs the validation on that action |

# Manual for NuvlaEdge validation testing

## Adding tests

To add tests to this framework there are some considerations to take into account:

1. Tests are based on Python unitTest standard library and TestCase class.
2. Tests are executed per module (e.g. basic, features, nuvla_operations, etc)
3. New validation tests must be places in a new file, named with test_* as
   prefix. The test class must extend the class ValidatorBase and be decorated
   with @validator('name_of_the_test') so the automatic system can find it. See
   any of the previously implemented test for reference.
4. Every TestCase must contain one single test_* method as they are intended to
   test a single specific functionally. However, if the testing target requires
   it, multiple operations can be performed.

## Integrating with CI

The NuvlaEdge validation system is composed by two main component: the TestBed
and the Validation Framework.

The validation framework, at the same time, consists in a combination of Python
UnitTests and Nuvla/NuvlaEdge remote deployment implementation with GitHub CI
actions.

A sample of initial tests have been developed and serve as base validation. If
these tests pass, the process will be counted passed.

To run the validation tests over a given repository, first the repo must be a
NuvlaEdge microservice or part of one
(e.g. a library). Secondly, a job must be added to the CI actions workflow of
the repository, following the next template:

```yaml
name: "Validation"

on:
  push:
    branches:
      - 'main'
  pull_request:
    types: [ready_for_review]
  workflow_dispatch:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref_name }}
  cancel-in-progress: true

env:
  VALIDATION_PACKAGE_NAME: "validation-latest-py3-none-any.whl"
  BRANCH_NAME: ${{ github.head_ref || github.ref_name || vars.GITHUB_REF_NAME }}

jobs:

  setup-matrix:
    runs-on: ubuntu-latest
    outputs:
      boards: ${{ steps.set-boards.outputs.boards }}
      tests: ${{ steps.set-tests.outputs.tests }}
    steps:
      - id: set-boards
        run: |
          echo "boards=${{ vars.TESTBED_BOARDS }}" >> $GITHUB_OUTPUT

      - id: set-tests
        run: |
          echo "tests=${{ vars.VALIDATION_TESTS }}" >> $GITHUB_OUTPUT

  run-validator:
    needs: setup-matrix
    strategy:
      matrix:
        board-config: ${{ fromJSON(needs.setup-matrix.outputs.boards) }}
        validation-type: ${{ fromJSON(needs.setup-matrix.outputs.tests) }}
      fail-fast: false
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
          python-version: '3.10'

      - name: Install Validation Framework dependency
        run: python -m pip install ${{ env.VALIDATION_PACKAGE_NAME }}  --force-reinstall

      - name: Setup results folder
        run: |
          mkdir -p results/temp/xml results/temp/json

      - name: Clear previous results
        run: |
          rm results/temp/xml/*.xml || true

      - name: Run Validation on board ${{ matrix.board-config }}
        run: |
          python -m validation_framework --target ${{ matrix.board-config }}.toml \
          --validator ${{ matrix.validation-type }} --repository ${{ github.event.repository.name }} \
          --branch ${{ env.BRANCH_NAME }} 

      - name: Publish Unit Test Results
        uses: EnricoMi/publish-unit-test-result-action/composite@v2
        if: always()
        with:
          check_name: "| ${{ matrix.board-config }} --- ${{ matrix.validation-type }} |"
          junit_files: "results/temp/xml/*.xml"
```

Where the first step, sets up the local python environment, the second installs
the required libraries (if not present) and the last triggers the execution of
the unittests. 
