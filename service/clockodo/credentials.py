from configparser import ConfigParser
from os.path import join, dirname


class CredentialsProvider(object):
    def __init__(self):
        config_parser = ConfigParser()
        with open(join(dirname(__file__), 'credentials.properties'), 'r') as cred:
            config_parser.read_file(cred)
            self.email = config_parser['credentials']['email']
            self.api_key = config_parser['credentials']['api_key']
