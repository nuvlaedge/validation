#!/bin/bash

# Create a shared volume among containers
docker volume create --driver local --opt type=tmpfs --opt device=/Users/runner/.ssh  testbed_keys

# Populate that volume with the ssh keys
docker container create --name copy_to_vol -v testbed_keys:/opt/ hello-world
docker cp ~/.ssh/ copy_to_vol:/opt/test
docker rm copy_to_vol

n=$(ls ~/validation/conf/targets | wc -l)
echo "Found ${n} devices"

for (( i = 0; i < n; i++ )); do
    docker run --detach --rm --name validation_runner_${i} --hostname validation_runner_${i} --label validation_runner --env RUNNER_TOKEN=$RUNNER_TOKEN --env ORGANIZATION=nuvlaedge  -v testbed_keys:/home/runner/.ssh/ validation-runner:0.0.1a1
done
