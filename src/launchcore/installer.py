from .downloader import download_files as download_files, download_file as download_file

def main(args, config) :
    url = config['download']['version_manifest']
    root = config['path']['root']
    if args.update :
        update(url, root)
    else :
        args.subparser.print_help()

def update(url, root) :
    out = download_file(url, root + '/versionlist/version_manifest.json', cache_dir = root + '/cache')
    if out[0] :
        print("success")
    else :
        print("fail")
