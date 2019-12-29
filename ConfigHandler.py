from configparser import ConfigParser
import os.path as path
import json


# Settings Config
class ConfigManager:
    config = ConfigParser()

    def __init__(self):
        if not path.exists('default.ini'):
            self.default = ConfigParser()
            self.create_default_config()
            print('Default config created')
        else:
            print('Default config exists, ignoring')
        self.load_config()
        self.save_config()

    def load_config(self):
        return ConfigManager.config.read(['default.ini', 'config.ini'])

    def save_config(self):
        with open('config.ini', 'w') as outfile:
            ConfigManager.config.write(outfile)

    def create_default_config(self):
        self.default['Settings'] = {
            'token': 'default',
            'client_id': 'default',
            'channel': '-1',
            'auto_kick': 'False',
            'name_change_protection': 'False',
            'kick_message': 'You have been kicked for having an offensive or vulgar user name, '
                            'please change your account name or contact the server administrator '
                            'if you believe this is an error. '
                            'https://support.discordapp.com/hc/en-us/articles/213480948-How-do-I-change-my-Username-',
            'welcome_message': '{0.mention}, Welcome to the server! Tell us about yourself :wink:'
        }

        with open('default.ini', 'w') as d_file:
            self.default.write(d_file)


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
        with open('exceptions.json', 'w') as outfile:
            json.dump(self.exceptions, outfile)

    def get_exceptions(self):
        return self.exceptions

    def add_exception(self, protocol, name):
        if protocol not in self.exceptions.keys():
            self.exceptions[protocol] = list()
            self.exceptions[protocol].append(name)
        else:
            self.exceptions[protocol].append(name)
        self.save_exceptions(self)

    def remove_exception(self, protocol, name):
        if name in self.exceptions[protocol]:
            self.exceptions[protocol].remove(name)
            self.save_exceptions(self)
            return True
        else:
            return False

    def contains(self, protocol, name):
        if protocol in self.exceptions.keys():
            return name in self.exceptions[protocol]
        else:
            return False
