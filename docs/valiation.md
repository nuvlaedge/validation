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



## 1. Automatic deployment

This validation step tests the main docker-compose.yml file. 
The deployment of the file must trigger the download and start of every NuvlaEdge microservice.

In this step the 

```shell
docker-compose -p edge_validation -f docker-compose.yml up -d
```

#### Expected results for ``` docker ps ```

| MicroService   | Status    | COMMAND                   | Name                                   |
|----------------|-----------|---------------------------|----------------------------------------|
| Agent          | (healthy) | ```./agent_main.py```     | ```${project_name}_agent_1```          |
| System-Manager | (healthy) | ```./manager_main.py```   | ```${project_name}_system-manager_1``` |
| VPN Client     | -         | ```./openvpn-client.sh``` | ```${project_name}_vpn-client_1```     |
|                |           |                           |                                        |

