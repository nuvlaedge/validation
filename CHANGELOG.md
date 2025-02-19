# Changelog

## [1.6.3](https://github.com/nuvlaedge/validation/compare/1.6.2...1.6.3) (2025-02-19)


### Bug Fixes

* **SSH:** Added skip for SSH operation on ONE 2560 devices ([4563bba](https://github.com/nuvlaedge/validation/commit/4563bba644b215b00765557050c450f5a2fb0fc4))
* **Update:** Added an exception to not run update tests on deployment repository ([8b485be](https://github.com/nuvlaedge/validation/commit/8b485be6d8f0f63c4bf8c264e82255dc169a309c))

## [1.6.2](https://github.com/nuvlaedge/validation/compare/1.6.1...1.6.2) (2025-02-18)


### Bug Fixes

* **Docker:** Fixed docker volume cleanup ([20d70e5](https://github.com/nuvlaedge/validation/commit/20d70e54f7061407228085793e7160131eba528a))
* **SSH:** Fixed ssh key issue ([39f1ec4](https://github.com/nuvlaedge/validation/commit/39f1ec49b8b782c8b0702c555063eb2d4000d86a))

## [1.6.1](https://github.com/nuvlaedge/validation/compare/1.6.0...1.6.1) (2025-02-14)


### Bug Fixes

* **Docker:** Fixed docker cleanup scripts ([ba3be07](https://github.com/nuvlaedge/validation/commit/ba3be07661a09dd6ec5faca8b02d200b424ace9d))

## [1.6.0](https://github.com/nuvlaedge/validation/compare/1.5.4...1.6.0) (2025-02-13)


### Features

* Added integration container and selective cleanup for integration with Ekinops 2560 device ([#68](https://github.com/nuvlaedge/validation/issues/68)) ([8f2a11d](https://github.com/nuvlaedge/validation/commit/8f2a11d59140edbbd5ce07307aac37777cca2b32))


### Bug Fixes

* **ci:** Fixed gateway build workflow ([ac170b6](https://github.com/nuvlaedge/validation/commit/ac170b69dd09e5ad0b4590fe9ce64b74ddaabcab))

## [1.5.4](https://github.com/nuvlaedge/validation/compare/1.5.3...1.5.4) (2024-12-19)


### Bug Fixes

* **kubernetes.py:** fix csr name by including uuid if needed ([37ae096](https://github.com/nuvlaedge/validation/commit/37ae0968ccb2bc2aed2c0653031adb063202f138))

## [1.5.3](https://github.com/nuvlaedge/validation/compare/1.5.2...1.5.3) (2024-11-19)


### Bug Fixes

* **K8s:** Fixed index out of range error in K8s driver ([da87e58](https://github.com/nuvlaedge/validation/commit/da87e584731d99c71c7e2bcc444a8d6adac214a5))

## [1.5.2](https://github.com/nuvlaedge/validation/compare/1.5.1...1.5.2) (2024-11-18)


### Bug Fixes

* Fixed update process for K8s NuvlaEdges. ([8c63a67](https://github.com/nuvlaedge/validation/commit/8c63a67b1336b435dc586fd74beeff2a458aa6d2))

## [1.5.1](https://github.com/nuvlaedge/validation/compare/1.5.0...1.5.1) (2024-11-14)


### Bug Fixes

* Fixed k8s bug on update operation ([#61](https://github.com/nuvlaedge/validation/issues/61)) ([6a1fdda](https://github.com/nuvlaedge/validation/commit/6a1fdda3b2cfffdd1fc810499beb9ad84e78a66e))
* Refactored nuvlabox-status retrieval to reduce Nuvla overload ([#63](https://github.com/nuvlaedge/validation/issues/63)) ([9a75ede](https://github.com/nuvlaedge/validation/commit/9a75ede06d766b2a0f302ae8c381e50ae4ecf304))

## [1.5.0](https://github.com/nuvlaedge/validation/compare/1.4.1...1.5.0) (2024-11-14)


### Features

* **operation:** Added NuvlaEdge update operation validation ([#59](https://github.com/nuvlaedge/validation/issues/59)) ([9e2e3d1](https://github.com/nuvlaedge/validation/commit/9e2e3d1faeda352da180ab8f092a9843d2099c12))

## [1.4.1](https://github.com/nuvlaedge/validation/compare/1.4.0...1.4.1) (2024-10-30)


### Bug Fixes

* **gh-runner:** Added docker cli and binding to container runner. Added docker-compose.yml to ease deployment of runners ([#57](https://github.com/nuvlaedge/validation/issues/57)) ([0cb9ab0](https://github.com/nuvlaedge/validation/commit/0cb9ab0f8704acfd2c049fe3ada93fa3308ed286))
* **k8s:** Fixed bug on kubeconfig. Always export KUBECONFIG env variable on command executions ([1a21f69](https://github.com/nuvlaedge/validation/commit/1a21f69800c43ebfb130d2ba3a1b7c7453a5bd7c))
* **runner:** Fixed a bug when sharing ssh keys from the host ([89c9a16](https://github.com/nuvlaedge/validation/commit/89c9a16401aed7e87ce8c8d8b44937a6f13434b8))

## [1.4.0](https://github.com/nuvlaedge/validation/compare/1.3.18...1.4.0) (2024-10-21)


### Features

* Add containerised version of the validator ([8b12b08](https://github.com/nuvlaedge/validation/commit/8b12b08e4c3d8f9602bcdba2ebada56fef49825f))


### Bug Fixes

* **ci:** Release workflow ([8f94d64](https://github.com/nuvlaedge/validation/commit/8f94d64fc7bd089012b6654500424272bb75d6a5))


### Continuous Integration

* Add manual workflow trigger to release ([1ff4dac](https://github.com/nuvlaedge/validation/commit/1ff4dac79fd92e889da367c85e4454bea45e30f3))
* Add release please tooling for release ([0c13a6f](https://github.com/nuvlaedge/validation/commit/0c13a6f2e94f6cc672e33a397a7b0e56cf09f63f))
* Fixed target Nuvladev repository and Github credential ([0931d6d](https://github.com/nuvlaedge/validation/commit/0931d6da785e16b688fc139c54f3136995f824f3))
