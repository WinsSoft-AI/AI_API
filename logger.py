import logging
import json
from datetime import datetime
from config import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)

request_logger = logging.getLogger("request_logger")
response_logger = logging.getLogger("response_logger")

req_handler = logging.FileHandler("logs/requests.log")
res_handler = logging.FileHandler("logs/responses.log")

req_handler.setFormatter(logging.Formatter("%(message)s"))
res_handler.setFormatter(logging.Formatter("%(message)s"))

request_logger.addHandler(req_handler)
response_logger.addHandler(res_handler)


def log_request(data: dict):
    data["timestamp"] = datetime.utcnow().isoformat()
    request_logger.info(json.dumps(data))


def log_response(data: dict):
    data["timestamp"] = datetime.utcnow().isoformat()
    response_logger.info(json.dumps(data))
