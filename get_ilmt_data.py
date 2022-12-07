import os
import sys
import base64
import logging
import subprocess

from no.api.datapowerapi import DatapowerAPI
from no.util import paramparser
from no.util.scperror import ScpError

logger = logging.getLogger(__name__)


def _saveFile(filepath, data):
    try:
        file = open(filepath, 'wb')
        file.write(data)
        file.close()
    except:
        logger.error("Error writing file")
    else:
        logger.info("Successfully wrote {}".format(filepath))


def _setLogConfig(debug: bool):
    if (debug):
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(filename)s %(funcName)s: %(message)s',
        level=level,
        datefmt='%Y-%m-%d %H:%M:%S')


def _send_file_to_ilmt_server(file, destination):
    try:
        p = subprocess.Popen(["scp", file, destination],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        # sts = os.waitpid(p.pid, 0)
        if "Permission denied" in repr(p.stderr.readline):
            raise ScpError("Permission denied")
    except subprocess.CalledProcessError as e:
        logger.error("Failed to send file to ILMT server")
        raise e
    except OSError as e:
        logger.error("Failed to send file to ILMT server")
        raise e
    except ScpError as e:
        logger.error("Permission denied")
        raise e
    else:
        logger.info("Successfully sendt {} to ILMT".format(file))


if __name__ == "__main__":
    args = paramparser._parse_cli_args()
    print(args)
    _setLogConfig(args.debug)

    if not args.ilmt_destination:
        logger.error("--ilmt_destination required")
        sys.exit(1)

    instanceerror = []
    for dpInstance in args.inventory_list:
        client = DatapowerAPI(dpInstance, args.username,
                              args.password, port=args.port)

        if not client.isAvailable():
            logger.info("{} is unavailable".format(dpInstance))
            instanceerror.append(dpInstance)
            continue

        logger.info("{}: Saving ilmt file".format(dpInstance))

        for file in client.get_all_ilmt_files():
            logger.info(dpInstance + ": Saving " + file["name"])
            # logger.debug(file)
            certificatedecoded = base64.b64decode(file["file"])

            _saveFile(file["name"], certificatedecoded)
            logger.info("File saved {}".format(file["name"]))
            _send_file_to_ilmt_server(file["name"], args.ilmt_destination)
            logger.info("{} sendt to ILMT server".format(file["name"]))
            client.delete_ilmt_file(file["name"])
            logger.info("Cleanup file {} on {}".format(
                file["name"], dpInstance))

    if len(instanceerror) > 0:
        logger.error(
            "main: Error occured. Some instances where unavailable: {}".format(instanceerror))
        sys.exit(1)
