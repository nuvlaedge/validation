# Custom actions runners

The validation framework is built with GitHub workflows as main trigger.

Thanks to GitHub actions the validation framework automatically handles
parallelization, concurrency and distribution of jobs (device and tests set).

Thanks to GitHub actions the validation framework automatically handles
parallelization, concurrency and distribution of jobs (device and tests set).

To grant parallelization we run one action runner per device. Then, when
generating the test matrix, the GitHub workflow parameter `runs-on:` is assigned
by device. This implies that jobs assigned to different devices can run in
parallel. It also guarantees that concurrent validation runs won't override an
existing validation in the given runner. If two jobs are assigned to the same
device, it will generate a first-in-first-served based queue.

## Action runner container

The container runs the GitHub actions agent as entrypoint while capturing the
exit codes in order to self remove from GitHub when the container exits.

In order to start a container the next environmental variables must be provided:

- $RUNNER_TOKEN: GitHub generates a token that allows the agent (GitHub) to
  subscribe itself to the runners list in a project
- $ORGANIZATION: the target organization for the runner
- $RUNNER_TARGET: defines to which device this runner is associated (e.g. rpi4,
  ubuntu_vm)
