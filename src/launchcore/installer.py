from .downloader import download_files as download_files, download_file as download_file
import json

def main(args, config) :
    url = config['download']['version_manifest']
    root = config['path']['root']
    if args.update :
        update(url, root)
    if args.list != None :
        list(root, args.list)
    if False :
        args.subparser.print_help()

def update(url, root) :
    out = download_file(url, root + '/versionlist/version_manifest.json', cache_dir = root + '/cache')
    if out[0] :
        print('success')
    else :
        print('fail')

def read_json(file: str) :
    with open(file, 'r', encoding = 'utf-8') as f :
        js = json.load(f)
    return js

def list(root, type) :
    show = []
    data = read_json(root + '/versionlist/version_manifest.json')
    if type == 'all' :
        for ver in data['versions'] :
            show.append('{:<25} {:<15}'.format(ver['id'], ver['type']))

    else :
        for ver in data['versions'] :
            if type == ver['type'] :
                show.append('{:<25} {:<15}'.format(ver['id'], ver['type']))

    if len(show) == 0 :
        print(f'不存在类型: {type}')
    else :
        print("{:<25} {:<15}".format('version name', 'type'))
        print("-" * 40)
        for line in show :
            print(line)
