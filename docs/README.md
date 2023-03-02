# Architecture and design

The NuvlaEdge validation framework design and the architecture of the supporting 
infrastructure can be consulted [here](architecture/README.md). 

# Validation framework usage

The goal of this framework is to provide a functional test utility for developers
so both NuvlaEdge releases and new implemented features are automatically
validated.

The system is automated via GitHub actions integrated in all NuvlaEdge repos,
including [deployment](https://github.com/nuvlaedge/deployment) which is the
release controller.

NuvlaEdge validation system is configured to trigger under three conditions:
1. push to 'main' branch
2. when a PR is converted from draft. Action name: `ready_for_review`
3. when manually triggered from any branch

Options 1. and 2. are in place as part of NuvlaEdge CI/CD system facilitating the
validation of new developments.

Option 3. allows for developers to run validations manually during development
process.

## Integration with GitHub CI actions

This service is developed in order to be used within an organization scope. The
organization should contain the validation repository.

The workflow action of this repository is in charge of updating the software in
the runner everytime there is a new push into main.

Then, trigger the validation tests the required container will have to contain a
job inside its GitHub workflow.

The GitHub runner is described [here](actions_runner/README.md).

# Tests

The process of the development and integration of the tests is
described [here](tests/README.md). That document also contains the list of the
existing validation tests.

# Testbed and Devices

The documentation on the testbed and of how to add a new device to the testbed is
described [here](testbed/README.md).
