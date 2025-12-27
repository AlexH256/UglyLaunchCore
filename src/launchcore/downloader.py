import requests
from tqdm import tqdm
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import sys

def download_file(url, dest_path, progress_bar=True):
    """
    下载单个文件到指定路径，显示进度条
    
    Args:
        url (str): 文件下载URL
        dest_path (str): 目标文件路径（包含文件名）
        progress_bar (bool): 是否显示进度条
    
    Returns:
        tuple: (success, message) 成功返回True和文件路径，失败返回False和错误信息
    """
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        dir_name = os.path.dirname(dest_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        
        total_size = int(response.headers.get('content-length', 0))
        chunk_size = 8192
        
        with open(dest_path, 'wb') as f:
            if progress_bar:
                filename = os.path.basename(dest_path)
                with tqdm(total=total_size, unit='B', unit_scale=True, 
                         desc=filename, leave=False, file=sys.stdout) as pbar:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            else:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
        
        return True, dest_path
    except requests.exceptions.RequestException as e:
        return False, f"下载失败: {e}"
    except OSError as e:
        return False, f"文件写入失败: {e}"
    except Exception as e:
        return False, f"未知错误: {e}"

def download_files(urls, dest_paths, max_workers=5, progress_bar=True):
    """
    并行下载多个文件，每个文件都有独立的进度条
    
    Args:
        urls (list): 下载URL列表
        dest_paths (list): 目标文件路径列表（长度必须与urls相同）
        max_workers (int): 最大并发下载数
        progress_bar (bool): 是否显示进度条
    
    Returns:
        list: 每个下载任务的结果列表，每个元素为(success, message)元组
    """
    if len(urls) != len(dest_paths):
        raise ValueError("urls和dest_paths长度必须相同")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for url, dest_path in zip(urls, dest_paths):
            future = executor.submit(download_file, url, dest_path, progress_bar)
            futures.append(future)
        
        results = []
        for future in futures:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append((False, f"任务执行异常: {e}"))
    
    return results

'''
def main():
    """命令行接口示例"""
    import argparse
    parser = argparse.ArgumentParser(description='并行下载多个文件')
    parser.add_argument('--urls', nargs='+', help='下载URL列表')
    parser.add_argument('--dest_paths', nargs='+', help='目标文件路径列表')
    parser.add_argument('--workers', type=int, default=5, help='并发数')
    
    args = parser.parse_args()
    
    if args.urls and args.dest_paths:
        results = download_files(args.urls, args.dest_paths, args.workers)
        for i, (success, msg) in enumerate(results):
            status = "成功" if success else "失败"
            print(f"文件{i+1}: {status} - {msg}")
    else:
        print("请提供URL列表和目标路径列表")

if __name__ == "__main__":
    main()
'''