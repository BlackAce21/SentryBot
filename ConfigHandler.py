from configparser import ConfigParser
import os.path as path
import json


# Settings Config
class ConfigManager:
    def __init__(self):
        if not path.exists('default.ini'):
            self.default = ConfigParser()
            self.create_default_config()
            print('Default config created')
        else:
            print('Default config exists, ignoring')
        self.config = ConfigParser()
        self.load_config()

    def load_config(self):
        return self.config.read(['default.ini', 'config.ini'])

    def save_config(self):
        with open('config.ini', 'w') as outfile:
            self.config.write(outfile)

    def create_default_config(self):
        self.default['Settings'] = {
            'token': 'default',
            'client_id': 'default',
            'channel': '-1'
        }

        with open('default.ini') as d_file:
            self.default.write(d_file)

    def get_config(self):
        return self.config


# JSON Exception Config
class ExceptionsManager:
    def __init__(self):
        self.exceptions = {}
        if path.exists('exceptions.json'):
            self.exceptions = self.load_exceptions()

    @staticmethod
    def load_exceptions():
        with open('exceptions.json') as infile:
            return json.load(infile)

    @staticmethod
    def save_exceptions(self):
        with open('exceptions.json') as outfile:
            json.dump(self.exceptions, outfile)

    def get_exceptions(self):
        return self.exceptions

    def add_exception(self, protocol, name):
        if protocol not in self.exceptions.keys():
            self.exceptions[protocol] = set()
            self.exceptions[protocol].add(name)
        else:
            self.exceptions[protocol].add(name)
        self.save_exceptions(self)

    def remove_exception(self, protocol, name):
        if name in self.exceptions[protocol]:
            self.exceptions[protocol].remove(name)
            self.save_exceptions(self)
            return True
        else:
            return False
