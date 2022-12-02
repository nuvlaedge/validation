#!/bin/bash

running_runners=$(docker ps -a -q --filter="label=validation_runner")

if [ -z "$running_runners" ]
then
  echo "No runners running"
else
  echo "Removing runners"
  docker stop ${running_runners}
fi
