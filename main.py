import argparse
import installer

def setup() :
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='command', required=True)

    parser_installer = subparsers.add_parser('installer', help = '下载管理器')
    parser_installer.add_argument('-U', '--update', action = 'store_true', help = '更新版本清单')
    parser_installer.set_defaults(func = installer.main, subparser = parser_installer)

    return parser

def main() :
    parser = setup()
    args = parser.parse_args()

    args.func(args)

if __name__ == '__main__' :
    main()