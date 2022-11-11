# NuvlaEdge validation architecture overview

The validation system aims to provide a base automated way of testing Engine, microservices and overall functionalities of the NuvlaEdge software. 
It grants a standard validation system based on Nuvla requirements and QoS promised by SixSq.

The validation system is composed by two main components: Validation software and TestBed.

**TestBed**: Cluster of devices integrated by the top 10 most used devices of SixSq clients.

**Validation Service**: A collection of microservices exposing a service (triggered on demand) that runs a set of pre-established tests on the testbed devices. 

