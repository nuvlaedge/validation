# Validation Service

The validation service provides an API server as entrypoint and deployment tools to run tests. At the same time, it has the test evaluation 
services which then report the tests.

The architecture proposal for the validation system is as follows:
- GitHub Runner
- GitHub action

Then, for each device and test a Validation framework will be deployed, each of them composed by:
- Validator
- Deployer

The main workflow of the validation system consists on having a API server entry point which can retrieve test results from the DB and at the same time trigger tests based on simple configuration files.

When the tests are triggered, the validator server runs the framework with a specific configuration (Possible configurations or look up table* synchronized between the server and the framework)

***Look up** tables consists in a set of predefined test setups and its corresponding configuration in the validator.



## Validation Services
Composition of microservices that compose the validation server.

## Validation Framework
The validation framework is an instance which runs during the lifetime of the validation process of a single test and exists afterwards.

It is composed by a deployer and a tester module. 

