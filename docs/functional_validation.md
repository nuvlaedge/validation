# Min. requirements validation

| #    |          Name           | Description                                                                              |
|:-----|:-----------------------:|------------------------------------------------------------------------------------------|
| 1    |  Automatic deployment   | The deployment of the NuvlaEdge must be successful with single docker compose command    |     
| 2    |       Activation        | The NuvlaEdge must automatically activate itself.                                        |     
| 3    |       Commission        | The NuvlaEdge must perform the commissioning process                                     |     
| 4    |    VPN Commissioning    | VPN keys signing and VPN connection success                                              |     
| 5    |  Pull job capabilities  | The engine must be capable of running pull jobs (deploy, update and remove)              |     
| 6    |  Push job capabilities  | The engine must be capable of running push jobs (deploy, update and remove)              |     
| 7    |  Min. telemetry report  | Check that the system is capable of reporting the minimum telemetry required             |     
| 8    |        Run time         | The system must keep running for a given time in order to consider the release validated |


##  Requirements
* ```Docker version > 18.10```
* ```Docker compose > 1.29.2```

## Test scenarios
1. Swarm enabled/disabled
2. Skipping minimum requirements
3. VPN enabled/disabled

## 1. Automatic deployment

This validation step tests the main docker-compose.yml file. 
The deployment of the file must trigger the download and start of every NuvlaEdge microservice.


In this step the following command should be executed

```shell
docker-compose -p edge_validation -f docker-compose.yml up -d
```

#### Expected results for ``` docker ps ```

| MicroService   | Status    | COMMAND                                                                           | Name                                     |
|----------------|-----------|-----------------------------------------------------------------------------------|------------------------------------------|
| Agent          | (healthy) | ```./agent_main.py```                                                             | ```${project_name}_agent_1```            |
| System-Manager | (healthy) | ```./manager_main.py```                                                           | ```${project_name}_system-manager_1```   |
| VPN Client     | -         | ```./openvpn-client.sh```                                                         | ```${project_name}_vpn-client_1```       |
| Job Engine     | (paused)  | ```/app/pause.py```                                                               | ```${project_name}_job-engine-lite_1```  |
| Compute API    | -         | ```./api.sh```                                                                    | ```${project_name}_compute-api_1```      |
| On Stop        | (paused)  | ```./on_stop_main.py pause```                                                     | ```${project_name}_on-stop_1```          |
| Data gateway   | -         | ```sh -c 'sleep 10 && /usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf'``` | ```data-gateway.1.${random_hash}```      |


## 2. Activation
Validation of the activation process of the NuvlaEdge.
After checking the system-requirements the engine should send the activation request. Then process the response accordingly. 


Cases depending on the state of the Edge resource instance:

1. Provided UUID -> Tries to activate
   1. Success: Saves the keys returned and continues
   2. Failed: Exit with error

2. Provided NuvlaEdge Keys -> Activation should be skipped and remote state checked.
   1. If NuvlaEdge state ACTIVATED -> Commission
   2. If state COMMISSIONED -> Start Telemetry

Total 6 test corner cases

## 3. Commission
Commissions the NuvlaBox resource. It first has to gather the remote NuvlaEdge resource state

Cases depending on the remote state:
1. NEW -> Go to activate
2. ACTIVATED -> Go to commission
3. COMMISSIONED -> Go to heartbeat
4. DECOMMISSIONED/ING -> EXIT with error 

Cases depending on the remote response

1. Forbidden result -> Means the remote resource either does not exist or the state is not what expected

Total 5 test corner cases


## 4. VPN Commissioning


## 5. Pull job capabilities
Always available. 

## 6. Push job capabilities
NEEDS VPN

## 7. Min. telemetry report


## 8. Run time
To pass the test the system must run for at least 24 hours with an availability of 95%