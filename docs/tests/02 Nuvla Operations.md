# 1. Reboot
Tests the Nuvla reboot operation

### Assertions

- Start NuvlaEdge
- Wait for commissioned and operational
- Launch reboot job in nuvla
- Wait for job to complete
- Wait for device to come back up
- Assert successful reboot
- Assert successful NuvlaEdge recovery

# 2. Deployment
Tests the deployment operation. Both in pull and push mode using two different tests

### Assertions
- Start NuvlaEdge
- Wait for commissioned and operational
- Trigger deployment
- Wait job success
- Wait deployment to be started
- Assert containers running
- Assert deployment health in Nuvla

*Repeat for both types of deployments*

# 3. SSH Management
Tests both Nuvla actions, add and remoke SSH keys

### Assertions
- Start NuvlaEdge
- Wait for commissioned and operational
- Trigger add ssh
- Assert job succeeded
- Assert key present in local ssh
- Trigger revoke ssh
- Assert job succeeded
- Assert key not present

# 4. Update
Tests the capacity of NuvlaReleases to reach the latest NuvlaVersion
This is a special tests that should be ran whenever deployment main branch receives a push

### Assertions
- Start NuvlaEdge on tagged release version
- Wait for commissioned and operational
- Trigger update pointing to nuvlaedge/deployment:main repository
- Assert job succeeded
- Assert NuvlaEdge container image versions match the requirements
