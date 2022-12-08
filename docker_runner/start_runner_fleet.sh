#!/bin/bash

n=$(ls ~/validation/conf/targets | wc -l)
echo "Found ${n} devices"

target_dir="../conf/targets/*.toml"
echo $file_names
for format_name in $(ls $target_dir)
do
    target_name=$( basename $format_name )
    target_name=${target_name/.toml/}
    echo "Starting runner for  $(basename $target_name)"
    docker run --detach --rm --name runner_${target_name} --hostname validation_runner_${target_name} --label validation_runner --env RUNNER_TOKEN=$RUNNER_TOKEN --env ORGANIZATION=nuvlaedge --env RUNNER_TARGET=$target_name -v /Users/runner/.ssh/:/home/runner/.ssh/ validation-runner:0.0.1a1
done
