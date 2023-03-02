# Testbed description

TODO.

# Adding a device to the validation system

There are some configurations that need to be edited:

- Create a new .toml file following the configuration of the already present
  in [targets](/conf/targets) and save it in that same folder.
- Update the file [start_runner_fleet.sh](/docker_runner/start_runner_fleet.sh)
  with the corresponding filename provided in the previous step. This will
  trigger the creation of a specific runner for this device when the script is
  run.
- Lastly, every repository workflow must be updated to contain the new file. In
  the strategy/matrix level of the workflow. 
 