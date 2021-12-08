import fileinput
import logging
import re

logging.basicConfig(level=logging.WARNING)

class NginxRequestStatistics:

    def __init__(self, data):
        self.remote_addr = data['remote_addr']
        self.time_local = data['time_local']
        self.http_verb = data['http_verb']
        self.url = data['url']
        self.status_code = data['status_code']
        self.body_bytes_sent = data['body_bytes_sent']
        self.http_referer = data['http_referer']
        self.user_agent = data['user_agent']
        self.request_length = data['request_length']
        self.request_time = data['request_time']
        self.proxy_upstream_name = data['proxy_upstream_name']
        self.proxy_alternative_upstream = data['proxy_alternative_upstream']
        self.upstream_addr = data['upstream_addr']
        self.upstream_response_length = data['upstream_response_length']
        self.upstream_response_time = data['upstream_response_time']
        self.upstream_status = data['upstream_status']
        self.request_id = data['request_id']

    def __repr__(self):
        return f"Request ID: {self.request_id}\n" \
               f"Remote address: {self.remote_addr}\n" \
               f"Start time: {self.time_local}\n" \
               f"Request URL: {self.url}\n" \
               f"Request VERB: {self.http_verb}\n" \
               f"Request status: {self.status_code}\n" \
               f"User agent: {self.user_agent}\n" \
               f"Request time: {self.request_time}\n" \
               f"Service: {self.proxy_upstream_name}\n"

class NginxLogParser:

    pattern = r'(?P<remote_addr>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(?P<time_local>\d{2}\/[A-Za-z]{3}\/\d{4}:\d{2}:\d{2}:\d{2} (\+|\-)\d{4})\] "(?P<http_verb>(\w+)) (?P<url>.+) HTTP/(2\.0|1\.1)" (?P<status_code>\d+) (?P<body_bytes_sent>\d+) "(?P<http_referer>.+)" "(?P<user_agent>.+)" (?P<request_length>\d+) (?P<request_time>[\.0-9]+) \[(?P<proxy_upstream_name>.+)\] \[(?P<proxy_alternative_upstream>.*)\] (?P<upstream_addr>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+) (?P<upstream_response_length>\d+) (?P<upstream_response_time>[\.0-9]+) (?P<upstream_status>\d+) (?P<request_id>[0-9a-f]+)'

    def __init__(self):
        self.parser = re.compile(self.pattern)

    def parse_stdin(self):
        for line in fileinput.input():
            yield self.parse(line)

    def parse(self, line):
        matches = self.parser.match(line)

        if not matches:
            logging.warning(f"[{line}] doesn't match pattern")
        else:
            stats = NginxRequestStatistics(matches.groupdict())
            logging.debug(stats)
            return stats
