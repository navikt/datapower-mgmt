# Datapower-mgmt
Python scripts used to automate against IBM DataPower.

Rest interface and xml interface need to be enabled.

## Parameters
Parameters available on all scripts

````
usage: <script> [-h] -i INVENTORY_LIST [INVENTORY_LIST ...] -u USERNAME -p PASSWORD [--port PORT] [--dir DIR] [--domain DOMAIN] [-c--config CONFIG] [-d] [--ignore_ssl] [--timeout TIMEOUT] [--ilmt_destination ILMT_DESTINATION]

Python lib for DataPower management

optional arguments:
  -h, --help            show this help message and exit
  -i INVENTORY_LIST [INVENTORY_LIST ...], --inventory INVENTORY_LIST [INVENTORY_LIST ...]
                        DataPower hosts
  -u USERNAME, --username USERNAME
                        Username
  -p PASSWORD, --password PASSWORD
                        password
  --port PORT           DataPower REST port. Use same port for all instances (Default 5444)
  --dir DIR             Path to directory where to store files (Default: current path)
  --domain DOMAIN       Select domain on DataPower appliance (Default domain: default)
  -c--config CONFIG     DataPower config file (Not in use)
  -d, --debug           Send debug messages to STDERR (Default False)
  --ignore_ssl          ignore_ssl
  --timeout TIMEOUT     Connection timeout
  --ilmt_destination ILMT_DESTINATION
                        Destination for ILMT server. user@host:/path
````
## Scripts
### Backup domain
Backup domain on DataPower. 
PORT needs to be set to the XML Management Interface
```` 
python3 backup_domain_on_appliance.py -i ${INVENTORY_LIST} -u ${USERNAME} -p ${PASSWORD} --dir ${DIR} --port ${PORT}
````

### Save all certificates in local:///pubcert
````
python3 savedatapowerpubcert.py -i ${INVENTORY_LIST} -u ${USERNAME} -p ${PASSWORD} --dir ${DIR} --port ${PORT}
````

### ILMT data
Script to get ILMT data
````
python3 get_ilmt_data.py -i ${INVENTORY_LIST} -u ${USERNAME} -p ${PASSWORD} --port ${PORT}
````

### DataPower status
Creates status.json which can be uploaded to [datapower-status](https://github.com/navikt/datapower-status)
````
python3 datapowerstatus.py -i ${INVENTORY_LIST} -u ${USERNAME} -p ${PASSWORD} --port ${PORT} --ilmt_destination "user@host:/path"
````

## Development
#### Local test appliance DataPower
Good guide to setup DataPower with docker on local desktop <https://github.com/ibm-datapower/datapower-tutorials/blob/master/getting-started/start-with-docker.md>

````
docker pull ibmcom/datapower:latest

docker run -it \
  -v $PWD/config:/drouter/config \
  -v $PWD/local:/drouter/local \
  -e DATAPOWER_ACCEPT_LICENSE=true \
  -e DATAPOWER_INTERACTIVE=true \
  -p 9090:9090 \
  -p 9022:22 \
  -p 5554:5554 \
  -p 8000-8010:8000-8010 \
  --name idg \
  ibmcom/datapower

configure; web-mgmt 0 9090;
````
