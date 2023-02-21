# NuvlaEdge engine validation

This repository contains the source code for the NuvlaEdge validation service.
The goal of the service is to execute a suite of tests over a given NuvlaEdge
version. The tests are performed automatically triggered by GitHub Actions. A
custom GitHub Runner managed by SixSq is used for the execution of the actions.

For details on the implemented tests, the validation framework usage, integration 
with GitHub CI Actions (and more) see [documentation](docs/README.md).

The current validation results can be seen [here](RESULTS.md).

# Repository reference

The following contains a depiction of the structure of the content files that
affect the non directly associated to validation of NuvlaEdge. This includes,
the testbed file description, the github action runners, etc. 

The repository is structured as follows:

* [.github](/.github) Contains the Github action runner workflow description to
  update the release of the package everytime a push is made against the main
  branch.
* [conf](/conf) Contains both the target device configuration and the releases
  configuration files
* [docker_runner](/docker_runner) Contains necessary files to create the GH
  self-hosted runner Docker image and deployment.
* [docs](/docs) Documentation related to the repository, architecture, howto's, 
  etc.
