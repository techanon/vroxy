from __future__ import unicode_literals
from configparser import ConfigParser
from asyncio import sleep
import time
import re
from os import path
from urllib.parse import urlparse

from aiohttp import web
from yt_dlp import YoutubeDL

from normalize import normalizeUrl


class PoolCount:
    def __init__(self):
        self.count = 0

    def add(self):
        self.count += 1

    def remove(self):
        self.count -= 1


class Item:
    def __init__(self, url, mode):
        self.original_url = url
        self.hostname = urlparse(url).hostname
        self.resolved_url = None
        self.resolved_id = None
        self.mode = mode
        self.expiry = 0
        self.processing = True

    def resolve(self, f):
        self.resolved_url = f['url']
        self.resolved_id = f['format_id']
        self.expiry = self.extractExpiry()
        self.processing = False

    def extractExpiry(self):
        p = expire_regex.search(self.resolved_url)
        if (p is not None):
            return int(p.group(1))
        return time.time() + 600 # default to 10 minutes
    


expire_regex = re.compile(r"exp(?:ir(?:es?|ation))?=(\d+)")
def format_selector(format_list, item):
    format_list.reverse()

    # explicitly filter for a specific format type when looking for HQ vimeo links
    if item.mode == 1 and item.hostname in ["vimeo.com"]:
        t_list = [
            f
            for f in format_list
            if str.startswith("hls_akafire-interconnect_quic", f["format_id"])
        ]
        if len(t_list) > 0:
            format_list = t_list

    best = format_list[0]
    print(best["url"])
    return best


config = ConfigParser({"server": {"host": "localhost", "port": "8008"}})
if path.isfile("./settings.ini"):
    config.read("settings.ini")

mode_map = {"default": 0, "0": 0, "high": 1, "1": 1, "low": 2, "2": 2}
cache_map = {}
sort_opts = {
    0: ["hasvid", "hasaud", "res:1080"],
    1: ["hasvid", "hasaud", "res:9001"],
    2: ["hasvid", "hasaud", "res:480"],
}

pool_max = 10
pool = PoolCount()


routes = web.RouteTableDef()

@routes.view("/")
class YTDLProxy(web.View):
    async def head(self):
        if not self.request.query.get("url"):
            return web.Response(status=404)
        return web.Response(status=302, headers={"Location": await self.resolveUrl()})

    async def get(self):
        if not self.request.query.get("url"):
            return web.Response(status=404, text="Missing Url Param")
        return web.Response(status=302, headers={"Location": await self.resolveUrl()})

    async def resolveUrl(self):
        mode = self.request.query.get("m") or "default"
        mode = mode_map[mode]
        url = normalizeUrl(self.request.query.get("url"))
        _id = f"{mode}~{url}"
        if _id in cache_map:
            item = cache_map[_id]
            if item.expiry < time.time():
                print("Cache expired")
                del cache_map[_id]
            else:
                # wait until the other request for the same url resolves, 
                # then use the cached url from that
                while item.processing:
                    await sleep(1)
                print(f"Resolving mode {mode} for url: {url}")
                print("Cache hit")
                print(item.resolved_url)
                print(f"{item.resolved_id} expires in {item.expiry - time.time()} seconds")
                return item.resolved_url or ""

        cache_map[_id] = item = Item(url, mode)

        # wait for an pool slot to open
        while pool.count >= pool_max:
            await sleep(1)

        ytdl_opts = {"quiet": True, "format_sort": sort_opts[mode]}
        with YoutubeDL(ytdl_opts) as ytdl:
            pool.add()
            print(f"Resolving mode {mode} for url: {url}")
            print("Fetching fresh info")
            result = ytdl.extract_info(url, download=False)
            format_item = format_selector(result["formats"], item)
            pool.remove()
            item.resolve(format_item)
            print(f"{item.resolved_id} expires in {item.expiry - time.time()} seconds")

        print("")
        return item.resolved_url or ""


app = web.Application()
app.add_routes(routes)
web.run_app(app, host=config["server"]["host"], port=config["server"]["port"])
