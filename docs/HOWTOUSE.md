# Manual for NuvlaEdge validation testing
The NuvlaEdge validation system is composed by two main component: the TestBed and the Validation Framework.

The validation framework, at the same time, consists in a combination of Python UnitTests and Nuvla/NuvlaEdge remote 
deployment implementation with GitHub CI actions.

A sample of initial tests have been developed and serve as base validation. If these tests pass, the process will be
counted passed. If any other test fails, the system will report them as  a warning.

To run the validation tests over a given repository, first the repo must be a NuvlaEdge microservice or part of one 
(e.g. a library). Secondly, a job must be added to the CI actions workflow of the repository, following the next schema:

```yaml
jobs:
  update-validator:
    runs-on: validation-runner  # This is the runner containing the updated validation service
    strategy:
      matrix:
        board-config: ["device_conf_1.toml", "device_conf_2.toml", "device_conf_3.toml", ...]

    steps:
      - name: Setup Python environment
        uses: actions/setup-python@v4
        with:
          python-version: '3.10.8'

      - name: Install dependencies
        working-directory: /path/to/validation_framework
        run: pip install -r requirements.txt

      - name: Run Validation on board ${{ matrix.board-config }}
        working-directory: /path/to/validation_framework
        run: python __main__.py --repo <repo_name> --branch <branch_name> --target_device ${{matrix.board-config}}
```

Where the first step, sets up the local python environment, the second installs the required libraries (if not present) 
and the last triggers the execution of the unittests. 
