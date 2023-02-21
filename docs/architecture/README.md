# NuvlaEdge validation architecture overview

The validation system aims to provide a base automated way of testing Engine,
microservices and overall functionalities of the NuvlaEdge software. It grants a
standard validation system based on Nuvla requirements and QoS promised by
SixSq.

The validation system is composed by two main components: Validation software
and TestBed.

**TestBed**: Cluster of devices integrated by the top 10 most used devices of
SixSq clients.

**Validation Service**: A collection of microservices triggered by GitHub
actions. When triggered, it will create a validation framework per configured
device and run a set of test batteries on that device. There are multiple typer
of battery tests depicted in the [tests](../tests/) folder.

# Validation Framework design

The validation framework implements a generic platform to perform validation
tests over the NuvlaEdge software.

The framework consists in two main components:

1. Base framework
2. Validation tests
3. GitHub action runners

![Validation workflow](../media/Architecture_Overview.jpg)

## 1. Base Framework

The first extends Python UnitTests providing a parent class which can easily be
extended. This service comes with a subset of tools:

- Remote device handler: TargetDevice
- NuvlaEdge release handler: ReleaseHandler
- Nuvla client interface: NuvlaClient

### TargetDevice

This tool provides an interface to run remote commands in the configured device.

### ReleaseHandler

Currently, implemented for Standard releases on nuvlaedge/deployment repo.
Controls the release to be tested. Checks and triggers the download of the
remote required files

### NuvlaClient

Interfaces the creation and removal of the Edges to be tested. Also allows for
configurations on different edge starts

## 2. Validation Tests

The actual test implementations. It always extends the ValidationBase class and
have to be decorated with @validator tag and a unique name. This notation allows
the system to recognize it as a test and include it in the test battery (
Corresponding folder).

## 3. GitHub Actions Runner

A custom GitHub runner with an updated version of the framework and the
preconfigured devices that runs one battery of tests at a time in all the
available devices. Available devices are those which configuration is stored in
the default folder and online (will be checked automatically)

# Testbed

TODO.