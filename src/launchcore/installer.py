from .downloader import download_files as download_files, download_file as download_file
import json
from pathlib import Path

def main(args, config) :
    url = config['download']['version_manifest']
    root = config['path']['root']
    
    if args.update :
        update(url, root)
    elif args.list != False :
        list_available(root, args.list)
    elif args.complete != False :
        install_necc(root, args.complete)
    elif args.install != False :
        judge = install_json(root, args.install)
        if judge :
            install_necc(root, args.install)
    else :
        args.subparser.print_help()

def update(url, root) :
    out = download_file(url, root + '/versionlist/version_manifest.json', cache_dir = root + '/.cache')
    if out[0] :
        print('success')
    else :
        print('fail')

def read_json(file) :
    with open(file, 'r', encoding = 'utf-8') as f :
        js = json.load(f)
    return js

def list_available(root, type) :
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
        print(f'cannot find: {type}')
    else :
        print("{:<25} {:<15}".format('version name', 'type'))
        print("-" * 40)
        for line in show :
            print(line)

def install_json(root, idd) :
    print('\nVERSION JOSN')
    data = read_json(root + '/versionlist/version_manifest.json')
    url = None
    for ver in data['versions'] :
        if ver['id'] == idd :
            url = ver['url']
    if url != None :
        print(f'download {id}.json')
        outcome = download_file(url, root + '/versions/' + idd + '/' + idd + '.json', cache_dir = root + '/.cache')
        result = outcome[0]
    else :
        result = False
        print(f'cannot find version: {idd}')
    
    return result
            
def install_necc(root, idd) :
    install_jar(root, idd)
    install_lib(root, idd)

def install_jar(root, idd) :
    version_json = read_json(root + '/versions/' + idd + '/' + idd + '.json')
    
    # 下载主文件
    print('\nMAIN FILE')
    path = root + '/versions/' + idd + '/' + idd + '.jar'
    if not _check(path) :
        print(f'download {idd}.jar')
        url = version_json['downloads']['client']['url']
        result = download_file(url, path, cache_dir = root + '/.cache')
        print()
    else :
        result = ('exist', idd)
        print(f'exist: {idd}.jar\n')
    
    return result

def install_lib(root, idd) :
    version_json = read_json(root + '/versions/' + idd + '/' + idd + '.json')

    # 下载库文件

    # 生成下载列表 检查缺失
    file_list = []
    url_list = []
    name_list = []
    for slicy in version_json['libraries'] :
        element = slicy['downloads']['artifact']
        name = slicy['name']
        path = root + '/libraries/' + element['path']
        if not _check(path) :
            file_list.append(path)
            url_list.append(element['url'])
            name_list.append(name)
        else :
            # print(f'exist: {name}')
            pass
    
    # 下载
    print('\nLIBRARIES')
    print('download')
    for n in name_list :
        print(n)
    num = len(url_list)
    print(f'total: {num}\n')
    
    if num >= 2 :
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
            result = download_files(urlss[i], filess[i], multi, cache_dir = root + '/.cache')
    elif num == 1 :
        result = [download_file(url_list[0], file_list[0], cache_dir = root + '/.cache')]
    else :
        result = 'finished'
    
    # 复查缺失
    lack = []
    for slicy in version_json['libraries'] :
        element = slicy['downloads']['artifact']
        name = slicy['name']
        path = root + '/libraries/' + element['path']
        if not _check(path) :
            lack.append(name)

    if len(lack) != 0 :
        print('\nfailures')
        for n in lack :
            print(n)
    
    return result

def _check(file) :
    path = Path(file)
    return path.is_file()