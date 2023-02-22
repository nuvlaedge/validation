# 1. Standard deployment

Validation process of the normal deployment of the NuvlaEdge. Checks basic
deployment and exit of the NuvlaEdge.

Includes fulfilling the minimum requirements and following the standard
procedure of the NuvlaEdge.

### Steps

- Start NuvlaEdge
- Wait for commissioned and operational
- Assert Activation + Commissioning successfully done
- Run for 5 min
- Assert containers running without restarts
    - If restart occurs, either prompt warning or fail
- Assert No telemetry loses

# 2. System restart

Validates the recovery capacities of the NuvlaEdge given a sudden restart

### Steps

- Start NuvlaEdge
- When commissioned and operational trigger hard reboot
- Wait until device comes back up
- Assert reboot and NuvlaEdge health. Status should be operational.