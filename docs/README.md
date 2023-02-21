# Architecture and design

The NuvlaEdge validation framework design and the architecture of the supporting 
infrastructure can be consulted [here](architecture/README.md). 

# Validation framework usage

The goal of this service is to provide a functional test utility for developers
so both NuvlaEdge releases and new implemented features are automatically
validated.

The system is automatized via GitHub actions integrated in all NuvlaEdge repos,
including [deployment](https://github.com/nuvlaedge/deployment) which is the
release controller.

## Validation integration with GitHub CI actions

This service is developed in order to be used within an organization scope. The
organization should contain the validation repository.

The workflow action of this repository is in charge of updating the software in
the runner everytime there is a new push into main.

Then, trigger the validation tests the required container will have to contain a
job inside its GitHub workflow.

# Tests

For the list of the tests see

## Developing and integrating tests

The process of the development and integration of the tests is
described [here](tests/README.md).

# Testbed and Devices

The documentation on the testbed and of how to add a new device to the testbed is
described [here](testbed/README.md).
