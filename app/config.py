

from configparser import ConfigParser
from os import path
import os

config = ConfigParser()
config["server"] = {
    "host": os.getenv("VROXY_HOST", "0.0.0.0"),
    "port": os.getenv("PORT", "8008"),
    "whitelist": os.getenv("VROXY_WHITELIST", ""),
    "auth_tokens": os.getenv("VROXY_AUTH_TOKENS", ""),
}
settings_file = path.join(path.dirname(__file__), "settings.ini");
if path.isfile(settings_file): config.read(settings_file)
del settings_file