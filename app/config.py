

from configparser import ConfigParser
from os import path
import os

config = ConfigParser()
config["server"] = {
    "host": os.getenv("VROXY_HOST", "0.0.0.0"),
    "port": os.getenv("PORT", "8008"),
    "whitelist": os.getenv("VROXY_WHITELIST", ""),
}
if path.isfile(path.join(path.dirname(__file__), "settings.ini")): 
    config.read(path.join(path.dirname(__file__), "settings.ini"))

def getConfig(): return config