import logging
import json

from no.api.datapowerapi import DatapowerAPI
from no.util import paramparser

logger = logging.getLogger(__name__)


def _setLogConfig(debug: bool):
    if (debug):
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(filename)s %(funcName)s: %(message)s',
        level=level,
        datefmt='%Y-%m-%d %H:%M:%S')

def _saveFile(filepath, data):
    try:
        file = open(filepath, 'w')
        file.write(data)
        file.close()
    except:
        print("Error writing file")
    else:
        print("Successfully wrote {}".format(filepath))

if __name__ == "__main__":
    args = paramparser._parse_cli_args()
    print(args)
    _setLogConfig(args.debug)

    instanceerror = []
    output = []
    logger.info("args.inventory: {}".format(args.inventory_list))

    for dpInstance in args.inventory_list:
        logger.info("Running against: " + dpInstance + " on port " + str(args.port))

        client = DatapowerAPI(dpInstance, args.username, args.password, port=args.port)
        if not client.isAvailable():
            logger.info("{} is unavailable".format(dpInstance))
            instanceerror.append(dpInstance)
            continue

        status = client.get_standby_status()
        logger.info("Status for {} {}".format(dpInstance, status['State']))

        firmware = client.get_firmwareVersion()
        uptime= client.get_date_time_status()
        logger.debug(("firmware {}".format(firmware['Version'])))
        logger.debug(("machine {}".format(firmware['MachineType'])))

        domains = []
        for domain in client.get_domains():
            domains.append(domain['name'])

        instancestatus = {'dpInstance': dpInstance,
                          'State': status['State'],
                          'Version': firmware['Version'],
                          'MachineType': firmware['MachineType'],
                          'Domains': domains,
                          'uptime': uptime['uptime2'],
                          'bootuptime2': uptime['bootuptime2']}
        #instancestatus['State'] = status['State']
        #instancestatus['Version'] = firmware['Version']
        #instancestatus['MachineType'] = firmware['MachineType']
        #instancestatus['DomainStatus'] = client.get_domains()

        output.append(instancestatus)
        #logger.debug(instancestatus)

    logger.debug(output)
    logger.info("Writing results to file")
    #_saveFile("status.json", json.dump(output))
    with open('status.json', 'w') as outfile:
        json.dump(output, outfile)
