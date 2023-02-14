# Repository reference

This file contains a depiction of the structure of the content files that affect the non directly associated to validation of nuvlaedge. 
This includes, the testbed file description, the github action runners, etc. The validation related documentation is writen in the file "HOWTOUSE.md".

The repository is structured as follows:


<!-- TOC -->
* [.github](/.github) Contains the Github action runner workflow description to update the release of the package everytime a push is made against the main branch.
* [conf](/conf) Contains both the target device configuration and the releases configuration files
* [docker_runner](/docker_runner) Contains necessary the files to create the GH self-hosted runner Docker image and deployment.
* [docs](/docs) This and more documentation related to the repository, architecture, howto's, etc.
<!-- TOC -->

## How to add a device to the validation system?

There are some configurations that need to be edited:

- Create a new .toml file following the configuration of the already present in [targets](/conf/targets) and save it in that same folder.
- Update the file [start_runner_fleet.sh](/docker_runner/start_runner_fleet.sh) with the corresponding filename provided in the previous step. This will trigger the creation of a specific runner for this device when the script is run.
- Lastly, every repository workflow must be updated to contain the new file. In the strategy/matrix level of the workflow. 