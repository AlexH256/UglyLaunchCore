import argparse
from launchcore import installer
import configparser

def read_config() :
    conf = configparser.ConfigParser()
    conf.read('config.ini')
    return conf

def setup() :
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='command', required=True)

    parser_installer = subparsers.add_parser('installer', help = '下载管理器')
    parser_installer.add_argument('-U', '--update', action = 'store_true', help = '更新版本清单')
    parser_installer.set_defaults(func = installer.main, subparser = parser_installer)

    return parser

def main() :
    parser = setup()
    config = read_config()
    args = parser.parse_args()

    args.func(args, config)

if __name__ == '__main__' :
    main()