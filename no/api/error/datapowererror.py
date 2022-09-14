import logging
logger = logging.getLogger(__name__)

class DataPowerError(Exception):
    def __init__(self, status_code: int, error: dict):
        self.status_code = status_code
        self.error_code = error.get("code")
        self.help = error.get("help")

        error_message = "{0} {1}. {2}".format(
            self.status_code, self.error_code, self.help
        )
        
        super().__init__(error_message)