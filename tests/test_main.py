import configparser
from launchcore import installer

def read_config() :
    conf = configparser.ConfigParser()
    conf.read('test_config.ini')
    return conf

installer.install_necc('.minecraft', '1.21.11')