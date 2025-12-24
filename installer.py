import configparser
import requests
import os
from urllib.parse import urlparse
from tqdm import tqdm

config = configparser.ConfigParser()
config.read("config.ini")

list_url = config["download"]["version_manifest"]
root_path = config["path"]["root_path"]

