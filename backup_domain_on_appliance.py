import base64
import json
import logging
import os
import sys
import time

import urllib3
from xml.dom import minidom

from no.util import paramparser

logger = logging.getLogger(__name__)


def _createbackupdir(path):
    try:
        logger.debug("_createbackupdir: " + path)
        os.makedirs(path)
    except FileExistsError as err:
        logger.debug("Backup path exists")
    except OSError as ose:
        logger.debug("Could not create path: %s" % path)
        logger.debug(ose)
        return False
    return True


def _setLogConfig(debug: bool):
    if (debug):
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(filename)s %(funcName)s: %(message)s',
        level=level,
        datefmt='%Y-%m-%d %H:%M:%S')


def _getSavePath(args):
    if not args:
        pwd = os.getcwd()
    else:
        pwd = args
    return "{}/backup/".format(pwd)


def _saveFile(filepath, data):
    try:
        file = open(filepath, 'wb')
        file.write(data)
        file.close()
    except:
        logger.error("Error writing file")
#    else:
#        logger.info("Successfully wrote {}".format(filepath))


def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f}{unit}"


def listToString(s):
    # initialize an empty string
    str1 = " "

    # return string
    return str1.join(s)


if __name__ == "__main__":
    args = paramparser._parse_cli_args()
    print(args)
    _setLogConfig(args.debug)

    savepath = _getSavePath(args.dir)
    logger.info("Backups are saved to: " + savepath)

    instanceerror = []
    dpUri = "/service/mgmt/current"

    timeout = urllib3.util.Timeout(total=args.timeout)
    logger.info("Connection timeout: {}s".format(timeout.connect_timeout))

    logger.info("Saving backup to {}".format(savepath))
    success = _createbackupdir(savepath)
    if not success:
        logger.error("Savepath is not writable.")
        sys.exit(1)

    for dpInstance in args.inventory_list:
        logger.info(f"Running against: {dpInstance} on port {str(args.port)}")
        # Build XML for SOMA call
        full_backup = '<?xml version="1.0" encoding="UTF-8"?><env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"><env:Body><dp:request xmlns:dp="http://www.datapower.com/schemas/management"><dp:do-backup format="ZIP"><dp:user-comment>Automated backup of %s</dp:user-comment><dp:domain name="%s"/></dp:do-backup></dp:request></env:Body></env:Envelope>' % (
            args.domain, args.domain)

        # Creating base64 authentication
        # b64_creds = base64.b64encode(args.username + ":" + args.password)
        _headers = {
            "Authorization": "Basic {}".format(
                base64.b64encode("{}:{}".format(
                    args.username, args.password).encode()).decode()
            )
        }

        cert_reqs = "CERT_NONE" if args.ignore_ssl else "CERT_REQUIRED"
        logger.info(f"{dpInstance}: ignore_ssl {str(args.ignore_ssl)}")
        # logger.debug(f"{dpInstance}: cert_reqs {cert_reqs}")

        _http = urllib3.HTTPSConnectionPool(
            dpInstance, args.port, headers=_headers, cert_reqs=cert_reqs, timeout=timeout
        )

        try:
            resp = _http.request(
                "POST", dpUri, body=full_backup, retries=False)
            logger.info(dpInstance + ": Response status " + str(resp.status))
            logger.info(dpInstance + ": Parsing response XML")

            if resp.status >= 400:
                logger.error(
                    f"{dpInstance}: Connection error {str(resp.status)}")
                instanceerror.append(dpInstance)
                continue
        except urllib3.exceptions.HTTPError as e:
            logger.error(f"{dpInstance} : Connection error")
            logger.error(e)
            instanceerror.append(dpInstance)
            continue

        try:
            dom = minidom.parseString(resp.data)
            logger.debug(dpInstance + ": Checking for dp:result auth failure")
            if dom.getElementsByTagName('dp:result')[0].firstChild.nodeValue == "Authentication failure":
                logger.error(dpInstance + ": Authentication failure")
                instanceerror.append(dpInstance)
                continue
        except IndexError as e:
            # Catch IndexError because dp:result does not exist
            logger.debug(
                f"{dpInstance}: IndexError because off dp:result Authentication failure. This is OK")

        try:
            logger.debug(dpInstance + ": Checking for dp:result ERROR")
            if dom.getElementsByTagName('dp:result')[0].firstChild.nodeValue == "ERROR":
                logger.error(
                    f"{dpInstance}: <dp:result>ERROR</dp:result> Check the appliance for error")
                instanceerror.append(dpInstance)
                continue
        except IndexError as e:
            # Catch IndexError because dp:result does not exist
            logger.debug(
                f"{dpInstance}: IndexError because off dp:result ERROR. This is OK")
            # logger.debug(resp.data)

        logger.debug(
            f"Checking unavailable instances before getting dp:file: {instanceerror}")
        try:
            logger.debug(f"{dpInstance}: Trying to get dp:file")
            encodedBackup = dom.getElementsByTagName(
                'dp:file')[0].firstChild.nodeValue
            if encodedBackup:
                logger.debug(f"{dpInstance}: <dp:file> found")
                logger.debug(f"{dpInstance}: encodedBackup found")
            else:
                logger.debug(f"{dpInstance}: <dp:file> not found")
        except IndexError as e:
            # Catch IndexError because dp:result does not exist
            logger.debug(f"{dpInstance}: where is dp:file?")
            logger.error(e)
            instanceerror.append(dpInstance)

        logger.debug(
            f"Checking unavailable instances after getting dp:file: {instanceerror}")

        backupFileName = f"{time.strftime('%Y-%m-%d_%H%M')}_backup_{dpInstance}_{args.domain}"

        # Decode the content and write it as ZIP
        logger.info(f"{dpInstance}: Decoding base64 file")
        decodedBackup = base64.b64decode(encodedBackup)

        logger.info(
            f"{dpInstance}: Writing decoded response to ZIP file ({human_readable_size(len(decodedBackup))})")
        _saveFile(savepath + backupFileName + ".zip", decodedBackup)

        # Finish
        logger.info(f"Backup finished for {dpInstance}")

    success = [e for e in args.inventory_list if e not in instanceerror]
    logger.info(f"Successfully backed up: {listToString(success)}")
    if len(instanceerror) > 0:
        logger.error(
            f"main: Error occured. Some instances where unavailable: {listToString(instanceerror)}")
        sys.exit(1)
    else:
        sys.exit(0)
