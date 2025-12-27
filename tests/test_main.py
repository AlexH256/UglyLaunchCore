from launchcore.downloader import download_files
import os
import shutil

urls = [
    "https://httpbin.org/image/jpeg",
    "https://httpbin.org/image/png",
    "https://httpbin.org/image/webp",
]

dest_paths = ["test_download_1.jpg", "test_download_2.png", "test_download_3.webp"]

cache_path = "cache"


def test_parallel_download_with_cache():
    """测试带缓存目录的并行下载"""
    # 清理可能存在的旧文件和缓存目录
    for path in dest_paths:
        if os.path.exists(path):
            os.remove(path)
    if os.path.exists(cache_path):
        shutil.rmtree(cache_path)

    # 执行并行下载
    results = download_files(urls, dest_paths, max_workers=3, cache_dir=cache_path)

    # 检查所有下载是否成功
    all_success = all(success for success, _ in results)
    assert all_success, f"部分下载失败: {results}"

    # 检查目标文件是否存在
    for path in dest_paths:
        assert os.path.exists(path), f"目标文件不存在: {path}"

    # 检查缓存目录是否被清理（应为空）
    if os.path.exists(cache_path):
        cache_contents = os.listdir(cache_path)
        assert len(cache_contents) == 0, f"缓存目录未清理: {cache_contents}"

    # 清理测试文件
    for path in dest_paths:
        if os.path.exists(path):
            os.remove(path)
    if os.path.exists(cache_path):
        shutil.rmtree(cache_path)

    print("测试通过：所有文件成功下载并移动，缓存目录已清理")


if __name__ == "__main__":
    test_parallel_download_with_cache()
