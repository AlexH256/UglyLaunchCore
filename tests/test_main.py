import configparser
from launchcore import installer

def read_config() :
    conf = configparser.ConfigParser()
    conf.read('test_config.ini')
    return conf

installer.list('.minecraft/versionlist/version_manifest.json', 'old_beta')