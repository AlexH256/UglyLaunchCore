from .downloader import download_files as download_files, download_file as download_file
import json
from pathlib import Path

def main(args, config) :
    url = config['download']['version_manifest']
    root = config['path']['root']
    check = True
    if args.update :
        update(url, root)
        check = False
    if args.list != None :
        list(root, args.list)
        check = False
    if check :
        args.subparser.print_help()

def update(url, root) :
    out = download_file(url, root + '/versionlist/version_manifest.json', cache_dir = root + '/cache')
    if out[0] :
        print('success')
    else :
        print('fail')

def read_json(file) :
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

def install_json(root, id) :
    data = read_json(root + '/versionlist/version_manifest.json')
    url = None
    print(id)
    for ver in data['versions'] :
        if ver['id'] == id :
            url = ver['url']
    if url != None :
        out = download_file(url, root + '/versions/' + id + '/' + id + '.json', cache_dir = root + '/cache')
        print(out[0])
    else :
        print(f'找不到版本: {id}')
            
def install_necc(root, id) :
    version_json = read_json(root + '/versions/' + id + '/' + id + '.json')
    
    # 下载主文件
    path = root + '/versions/' + id + '/' + id + '.jar'
    if not check(path) :
        url = version_json['downloads']['client']['url']
        out = download_file(url, path, cache_dir = root + '/cache')
        print(out[0])
    else :
        print(f'{id}.jar文件已存在')

    # 下载库文件

    # 生成下载列表
    file_list = []
    url_list = []
    for slicy in version_json['libraries'] :
        element = slicy['downloads']['artifact']
        path2 = root + '/libraries/' + element['path']
        if not check(path2) :
            file_list.append(path2)
            url_list.append(element['url'])
    
    num = len(url_list)
    print(num)
    filess = []
    urlss = []
    multi = 32
    for i in range(num // multi) :
        filess.append(file_list[i:i + multi])
        urlss.append(url_list[i:i + multi])
    more = num % multi
    filess.append(file_list[(- more):])
    urlss.append(url_list[(- more):])

    for i in range(len(urlss)) :
        out = download_files(urlss[i], filess[i], multi, cache_dir = root + '/cache')
        print(out[0])

def check(file) :
    path = Path(file)
    return path.is_file()