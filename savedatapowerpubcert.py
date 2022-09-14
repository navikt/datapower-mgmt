import os, sys
import base64
import json
from datetime import datetime
import logging

from no.api.datapowerapi import DatapowerAPI
from no.util import paramparser

logger = logging.getLogger(__name__)

def _createcertificatedir(path):
    try:
        os.makedirs(path)
    except OSError as ose:
        print("Could not create path: %s" % path)
        print(ose)
    else:
        print("Successfully created dir: %s" % path)

def _saveFile(filepath, data):
    try:
        file = open(filepath, 'wb')
        file.write(data)
        file.close()
    except:
        print("Error writing file")
    else:
        print("Successfully wrote {}".format(filepath))

def _setLogConfig(debug: bool):
    if (debug):
        level=logging.DEBUG
    else:
        level=logging.INFO
    
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(filename)s %(funcName)s: %(message)s',
        level=level,
        datefmt='%Y-%m-%d %H:%M:%S')

def _getSavePath(args):
    date = datetime.now().strftime("%G%m%d-%H%M")
    if not args:
        pwd = os.getcwd()
    else:
        pwd = args
    return "{}/pubcert/{}".format(pwd,date)

if __name__ == "__main__":
    args = paramparser._parse_cli_args()
    print(args)
    _setLogConfig(args.debug)

    savepath = _getSavePath(args.dir)
    logger.debug("SavePath: " + savepath)
    instanceerror = []

    for dpInstance in args.inventory_list:
        client = DatapowerAPI(dpInstance, args.username, args.password, port = args.port)
        dir = savepath + "_" + dpInstance
        
        if not client.isAvailable():
            logger.info("{} is unavailable".format(dpInstance))
            instanceerror.append(dpInstance)
            continue

        logger.debug("{}: Saving pubcerts to {}".format(dpInstance,dir))
        _createcertificatedir(dir)

        for file in client.get_all_pubcert():
            logger.info(dpInstance + ": Saving " + file["name"])
            logger.debug(file)
            certificatedecoded = base64.b64decode(file["file"])

            _saveFile(dir +"/" + file["name"], certificatedecoded)

    if len(instanceerror)>0:
        logger.error("main: Error occured. Some instances where unavailable: {}".format(instanceerror))
        sys.exit(1)
       
