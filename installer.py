import configparser
import requests
import os
from urllib.parse import urlparse

config = configparser.ConfigParser()
config.read("config.ini")

list_url = config["download"]["version_manifest"]
root_path = config["path"]["root_path"]

def download_file(url, save_dir):
    response = requests.get(url)
    response.raise_for_status()
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    if not filename:
        filename = "downloaded_file"
    save_path = os.path.join(save_dir, filename)
    os.makedirs(save_dir, exist_ok=True)
    with open(save_path, 'wb') as f:
        f.write(response.content)
    print(f"Downloaded {filename} to {save_path}")

download_file(list_url, root_path)