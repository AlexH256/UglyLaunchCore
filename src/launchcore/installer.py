import configparser
from .downloader import download_files as download_files, download_file as download_file

config = configparser.ConfigParser()
config.read('config.ini')

list_url = config['download']['version_manifest']
root_path = config['path']['root_path']


def main(args) :
    if args.update :
        update()
    else :
        args.subparser.print_help()

def update() :
    out = download_file(list_url, root_path + '/versionlist/version_manifest.json')
    if out[0] :
        print("success")
    else :
        print("fail")
