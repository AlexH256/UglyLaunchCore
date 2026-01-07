import requests
from tqdm import tqdm
import os
import shutil
import uuid
from concurrent.futures import ThreadPoolExecutor
import sys
from typing import Tuple, List, Optional

CHUNK_SIZE = 8192  # 下载块大小（字节）


def _ensure_dir_exists(path: str) -> None:
    """确保目录存在，如果路径为空则不创建"""
    if path:
        os.makedirs(path, exist_ok=True)


def _cleanup_file(path: str) -> None:
    """清理单个文件，如果存在则删除，忽略错误"""
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass


def _cleanup_files(paths: List[str]) -> None:
    """清理多个文件"""
    for path in paths:
        _cleanup_file(path)


def download_file(
    url: str,
    dest_path: str,
    progress_bar: bool = True,
    cache_dir: Optional[str] = None,
    skip_move: bool = False,
) -> Tuple[bool, str]:
    """
    下载单个文件到指定路径，显示进度条

    Args:
        url (str): 文件下载URL
        dest_path (str): 目标文件路径（包含文件名）
        progress_bar (bool): 是否显示进度条
        cache_dir (str, optional): 缓存目录路径，如果提供则先下载到缓存目录，全部完成后移动到目标位置
        skip_move (bool, optional): 如果为True且cache_dir已提供，则只下载到缓存目录，不移动文件

    Returns:
        tuple: (success, message) 成功返回True和文件路径（或缓存路径），失败返回False和错误信息。
    """

    cache_path: str = ""
    try:
        # 确定最终下载路径

        if cache_dir is not None:
            # 创建缓存目录
            _ensure_dir_exists(cache_dir)
            # 生成唯一缓存文件名
            dest_filename = os.path.basename(dest_path)
            unique_suffix = uuid.uuid4().hex[:8]
            cache_filename = f"{dest_filename}.tmp.{unique_suffix}"
            cache_path = os.path.join(cache_dir, cache_filename)
            download_target = cache_path
        else:
            download_target = dest_path

        # 确保目标目录存在
        _ensure_dir_exists(os.path.dirname(download_target))

        # 下载文件
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        chunk_size = CHUNK_SIZE

        with open(download_target, "wb") as f:
            if progress_bar:
                filename = os.path.basename(dest_path)
                with tqdm(
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    desc=filename,
                    leave=True,
                    file=sys.stdout,
                    ncols=100,
                    ascii=True,
                    bar_format="{desc:20.20} {n_fmt:>10} {rate_fmt:>12} {remaining:>5} [{bar:20}] {percentage:3.0f}%",
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            else:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)

        # 处理缓存移动
        if cache_dir is not None:
            if skip_move:
                # 不移动，返回缓存路径
                return True, cache_path
            else:
                # 移动文件到目标位置
                try:
                    # 确保目标目录存在
                    _ensure_dir_exists(os.path.dirname(dest_path))
                    shutil.move(cache_path, dest_path)
                except Exception as move_error:
                    # 移动失败，删除缓存文件
                    try:
                        if os.path.exists(cache_path):
                            os.remove(cache_path)
                    except OSError:
                        pass
                    return False, f"文件移动失败: {move_error}"
                # 移动成功，返回目标路径
                return True, dest_path

        # 直接下载到目标路径的情况
        return True, dest_path

    except requests.exceptions.RequestException as e:
        # 下载失败，清理可能已创建的缓存文件
        _cleanup_file(cache_path)
        return False, f"下载失败: {e}"
    except OSError as e:
        _cleanup_file(cache_path)
        return False, f"文件写入失败: {e}"
    except Exception as e:
        _cleanup_file(cache_path)
        return False, f"未知错误: {e}"


def download_files(
    urls: List[str],
    dest_paths: List[str],
    max_workers: int = 5,
    progress_bar: bool = True,
    cache_dir: Optional[str] = None,
) -> List[Tuple[bool, str]]:
    """
    并行下载多个文件，每个文件都有独立的进度条

    Args:
        urls (list): 下载URL列表
        dest_paths (list): 目标文件路径列表（长度必须与urls相同）
        max_workers (int): 最大并发下载数
        progress_bar (bool): 是否显示进度条
        cache_dir (str, optional): 缓存目录路径，如果提供则先下载到缓存目录，全部完成后移动到目标位置

    Returns:
        list: 每个下载任务的结果列表，每个元素为(success, message)元组
    """

    if len(urls) != len(dest_paths):
        raise ValueError("urls和dest_paths长度必须相同")

    # 如果没有缓存目录，直接使用原逻辑
    if cache_dir is None:
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

    # 使用缓存目录的情况
    _ensure_dir_exists(cache_dir)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for url, dest_path in zip(urls, dest_paths):
            future = executor.submit(
                download_file, url, dest_path, progress_bar, cache_dir, True
            )
            futures.append(future)

        # 收集结果
        results = []
        cache_paths = []
        success_count = 0
        for future in futures:
            try:
                success, message = future.result()
                results.append((success, message))
                if success:
                    success_count += 1
                    cache_paths.append(message)  # 缓存路径
                else:
                    cache_paths.append(None)
            except Exception as e:
                results.append((False, f"任务执行异常: {e}"))
                cache_paths.append(None)

        # 判断是否全部成功
        if success_count == len(urls):
            # 全部成功，移动文件
            for i, (dest_path, cache_path) in enumerate(zip(dest_paths, cache_paths)):
                if cache_path is None:
                    continue
                try:
                    _ensure_dir_exists(os.path.dirname(dest_path))
                    shutil.move(cache_path, dest_path)
                except Exception as move_error:
                    # 移动失败，更新结果
                    results[i] = (False, f"文件移动失败: {move_error}")
            # 清理缓存目录（删除可能残留的文件）
            _cleanup_files(cache_paths)
        else:
            # 有失败，清理已下载的缓存文件
            _cleanup_files([cp for cp in cache_paths if cp is not None])

    return results
