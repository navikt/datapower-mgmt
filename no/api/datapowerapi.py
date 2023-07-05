from no.api.error.datapowererror import DataPowerError
import urllib3
import json
import logging
import base64

logger = logging.getLogger(__name__)


class DatapowerAPI:
    def __init__(self, hostname: str, username: str, password: str, port: int = 5554):
        self.hostname = hostname
        # port = port if port else 5554

        self._headers = {
            "Authorization": "Basic {}".format(
                base64.b64encode("{}:{}".format(
                    username, password).encode()).decode()
            ),
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        logging.debug("hostname: " + hostname)
        logging.debug("port: " + str(port))
        self._http = urllib3.HTTPSConnectionPool(
            hostname, port, headers=self._headers
        )

    def isAvailable(self):
        try:
            resp = self._request()  # defaults to GET on /
        except urllib3.exceptions.HTTPError as e:
            logger.info("{} is unavailable".format(self.hostname))
            logger.debug(e)
            return False
        return True

    # Get Application domains
    def get_domains(self):
        resp = self._request("GET", "/mgmt/domains/config/")
        domains = json.loads(resp.data.decode("utf-8"))
        return domains['domain']
    
    def get_domain_mAdminState(self, domain):
        resp = self._request("GET", f"/mgmt/config/default/Domain/{domain}")
        domain = json.loads(resp.data.decode("utf-8"))
        return domain['Domain']['mAdminState']

    # Get pubcert files
    def get_all_pubcert(self):
        resp = self._request("GET", "/mgmt/filestore/default/pubcert")
        # logger.debug(resp.data)
        files = json.loads(resp.data)

        b64files = []
        for file in files["filestore"]["location"]["file"]:
            logger.debug("Get info for: " + file["name"])
            filename = file["name"]
            href = file["href"]
            b64files.append(self._extract_b64_file(filename, href))

        logger.debug("Got all certificates.")
        logger.debug(b64files)
        return b64files

    def get_all_ilmt_files(self):
        resp = self._request("GET", "/mgmt/filestore/default/local/ilmt/output")
        # logger.debug(resp.data)
        files = json.loads(resp.data)

        b64files = []
        if "file" not in files["filestore"]["location"]:
            return []

        if not isinstance(files["filestore"]["location"]["file"], list):
            logger.debug("file is not an array. Only one file")
            file = files["filestore"]["location"]["file"]
            b64files.append(self._extract_b64_file(file["name"], file["href"]))
            return b64files

        logger.debug("Number of ILMT files {}".format(len(files["filestore"]["location"]["file"])))
        for file in files["filestore"]["location"]["file"]:
            logger.debug("Get info for: " + file["name"])
            filename = file["name"]
            href = file["href"]
            b64files.append(self._extract_b64_file(filename, href))

        logger.debug("Got all ILMT files")
        logger.debug(b64files)
        return b64files

    def delete_ilmt_file(self, filename):
        resp = self._request("DELETE", "/mgmt/filestore/default/local/ilmt/output/{}".format(filename))
        logger.debug(resp.data)
        status = json.loads(resp.data)
        return status["result"]

    def get_standby_status(self):
        resp = self._request("GET", "/mgmt/status/default/StandbyStatus2")
        logger.debug(resp.data)
        status = json.loads(resp.data)
        return status['StandbyStatus2']

    def get_firmwareVersion(self):
        resp = self._request("GET", "/mgmt/status/default/FirmwareVersion3")
        logger.debug(resp.data)
        firmware = json.loads(resp.data)
        return firmware['FirmwareVersion3']

    def get_date_time_status(self):
        resp = self._request("GET", "/mgmt/status/default/DateTimeStatus")
        logger.debug(resp.data)
        status = json.loads(resp.data)
        return status['DateTimeStatus']

    def get_domain_status(self):
        resp = self._request("GET", "/mgmt/status/default/DomainStatus")
        logger.debug(resp.data)
        status = json.loads(resp.data)
        return status['DomainStatus']

    def get_domain_version(self, domain):
        resp = self._request("GET", f"/mgmt/status/{domain}/local/version")
        logger.debug(resp.data)
        response = json.loads(resp.data)
        version = base64.b64decode(response["file"])
        return version

    def get_interface_bytype_ipaddress(self, type, name):
        resp = self._request(
            "GET", f"/mgmt/config/default/${type}/${name}/IPAddress")
        logger.debug(resp.data)
        status = json.loads(resp.data)
        interfaces = {}
        interfaces["Interface"] = type
        interfaces["Name"] = name
        interfaces["IPAddress"] = status['IPAddress']
        return interfaces

    def _extract_b64_file(self, filename, href):
        fileresp = self._request("GET", href)
        b64file = json.loads(fileresp.data)
        filemap = {"name": filename, "file": b64file["file"]}
        return filemap

    def _request(self, method="GET", endpoint="/", data=None):
        logger.info("{} {}".format(method, endpoint))
        if data is not None:
            logger.debug("Data posting " + data + "to " + endpoint)
            data = json.dumps(data).encode("utf-8")

        try:
            resp = self._http.request(method, endpoint, body=data, retries=False)
            logger.debug("Response status " + str(resp.status))
            if resp.status >= 400:
                try:
                    data = json.loads(resp.data)
                except json.JSONDecodeError:
                    data = {"error": resp.status,
                            "help": "A server error occurred."}
                raise DataPowerError(resp.status, data)
        except urllib3.exceptions.HTTPError as e:
            raise e
        else:
            logging.debug("End of request {} {}".format(str(resp.status), endpoint))
            logger.debug(resp.status)
            # logger.debug(resp.data)
            return resp
