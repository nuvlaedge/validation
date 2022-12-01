#!/bin/bash

ORGANIZATION=$ORGANIZATION
#ACCESS_TOKEN=$ACCESS_TOKEN

#REG_TOKEN=$(curl -sX POST -H "Authorization: token ${ACCESS_TOKEN}" https://api.github.com/orgs/${ORGANIZATION}/actions/runners/registration-token | jq .token --raw-output)
REG_TOKEN=$RUNNER_TOKEN

cd /home/runner/actions-runner

echo ${ORGANIZATION}

./config.sh --unattended --url https://github.com/${ORGANIZATION} --token ${REG_TOKEN} --replace --name ${HOSTNAME} --labels validation-runner

cleanup() {
    echo "Removing runner..."
    ./config.sh remove --token ${REG_TOKEN}
}

trap 'cleanup; exit 143' SIGTERM
trap 'cleanup; exit 130' INT

./run.sh & wait $!
