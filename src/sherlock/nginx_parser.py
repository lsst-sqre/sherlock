import fileinput
import logging
import re
from typing import Generator, Optional

logging.basicConfig(level=logging.WARNING)


NGINX_LOG_REGEXP = (
    r"(?P<remote_addr>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) "
    r"- "
    r"- "
    r"\[(?P<time>\d{2}\/[A-Za-z]{3}\/\d{4}:\d{2}:\d{2}:\d{2} (\+|\-)\d{4})\] "
    r'"(?P<http_verb>(\w+)) (?P<url>.+) HTTP/(2\.0|1\.1)" '
    r"(?P<status_code>\d+) "
    r"(?P<body_bytes_sent>\d+) "
    r'"(?P<http_referer>.+)" '
    r'"(?P<user_agent>.+)" '
    r"(?P<request_length>\d+) "
    r"(?P<request_time>[\.0-9]+) "
    r"\[(?P<proxy_upstream_name>.+)\] "
    r"\[(?P<proxy_alternative_upstream>.*)\] "
    r"(?P<upstream_addr>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+) "
    r"(?P<upstream_response_length>\d+) "
    r"(?P<upstream_response_time>[\.0-9]+) "
    r"(?P<upstream_status>\d+) "
    r"(?P<request_id>[0-9a-f]+)"
)


class NginxRequestStatistics:
    def __init__(self, data: dict) -> None:
        """Initialize all the fields.

        Note: the order of these fields is also the order in the dataframe."""
        self.time = data["time"]
        self.service_name = data["proxy_upstream_name"]
        self.http_verb = data["http_verb"]
        self.status_code = int(data["status_code"])
        self.url = data["url"]
        self.body_bytes_sent = int(data["body_bytes_sent"])
        self.request_length = int(data["request_length"])
        self.request_time = float(data["request_time"])
        self.upstream_addr = data["upstream_addr"]
        self.upstream_response_length = int(data["upstream_response_length"])
        self.upstream_response_time = float(data["upstream_response_time"])
        self.upstream_status = data["upstream_status"]
        self.request_id = data["request_id"]
        self.http_referer = data["http_referer"]
        self.proxy_alternative_upstream = data["proxy_alternative_upstream"]
        self.remote_addr = data["remote_addr"]
        self.user_agent = data["user_agent"]

    def __repr__(self) -> str:
        return (
            f"Request ID: {self.request_id}\n"
            f"Remote address: {self.remote_addr}\n"
            f"Start time: {self.time}\n"
            f"Request URL: {self.url}\n"
            f"Request VERB: {self.http_verb}\n"
            f"Request status: {self.status_code}\n"
            f"User agent: {self.user_agent}\n"
            f"Request time: {self.request_time}\n"
            f"Service: {self.service_name}\n"
        )


class NginxLogParser:
    def __init__(self) -> None:
        self.parser = re.compile(NGINX_LOG_REGEXP)

    def parse_stdin(
        self,
    ) -> Generator[Optional[NginxRequestStatistics], None, None]:
        for line in fileinput.input():
            yield self.parse(line)

    def parse(self, line: str) -> Optional[NginxRequestStatistics]:
        matches = self.parser.match(line)

        if not matches:
            logging.info(f"[{line}] doesn't match pattern")
            return None
        else:
            stats = NginxRequestStatistics(matches.groupdict())
            logging.debug(stats)
            return stats
