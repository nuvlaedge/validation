#!/bin/bash


ORGANIZATION=${ORGANIZATION:-nuvlaedge}
# Device to be targeted by this runner
RUNNER_TARGET=$RUNNER_TARGET
REG_TOKEN=$RUNNER_TOKEN

# Commented for a future automation with organization level token
#ACCESS_TOKEN=$ACCESS_TOKEN
#REG_TOKEN=$(curl -sX POST -H "Authorization: token ${ACCESS_TOKEN}" https://api.github.com/orgs/${ORGANIZATION}/actions/runners/registration-token | jq .token --raw-output)

cd /home/runner/actions-runner

echo ${ORGANIZATION}

./config.sh --unattended --url https://github.com/${ORGANIZATION} --token ${REG_TOKEN} --replace --name ${HOSTNAME} --labels validation-runner,${RUNNER_TARGET}

cleanup() {
    echo "Removing runner..."
    ./config.sh remove --token ${REG_TOKEN}
}

trap 'cleanup; exit 143' SIGTERM
trap 'cleanup; exit 130' INT

./run.sh & wait $!
