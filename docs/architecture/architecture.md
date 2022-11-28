# NuvlaEdge validation architecture overview

The validation system aims to provide a base automated way of testing Engine, microservices and overall functionalities of the NuvlaEdge software. 
It grants a standard validation system based on Nuvla requirements and QoS promised by SixSq.

The validation system is composed by two main components: Validation software and TestBed.

**TestBed**: Cluster of devices integrated by the top 10 most used devices of SixSq clients.

**Validation Service**: A collection of microservices trigger by GitHub actions. When triggered, it will create a validation 
framework per configured device and run a set of test batteries on that device. There are multiple typer of battery 
tests depicted in the [tests](../tests/) folder. 

