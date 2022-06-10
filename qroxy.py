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
    def __init__(self, url, sort):
        self.original_url = url
        self.hostname = urlparse(url).hostname
        self.resolved_url = None
        self.resolved_id = None
        self.resolved_format = None
        self.sort = sort
        self.expiry = 0
        self.processing = True

    def resolve(self, f):
        if self.sort:
            f = f["formats"][-1]
        self.resolved_url = f["url"]
        self.resolved_id = f["format_id"]
        self.resolved_format = f["format"]
        self.expiry = self.extractExpiry()
        self.processing = False

    def extractExpiry(self):
        p = expire_regex.search(self.resolved_url)
        if p is not None: return int(p.group(1))
        return time.time() + 600  # default to 10 minutes


expire_regex = re.compile(r"exp(?:ir(?:es?|ation))?=(\d+)")


def format_selector(format_list, item):
    # print("", flush=True)

    best = format_list[0]
    print(best["url"])
    return best


config = ConfigParser({"server": {"host": "localhost", "port": "8008"}})
if path.isfile("./settings.ini"):
    config.read("settings.ini")

mode_map = {
    # default
    "0": 0,
    # avhigh
    "1": 1,
    # avlow
    "2": 2,
    # hqvidcompat
    "3": 3,
    # hqvidbest
    "4": 4,
}
cache_map = {}
sort_opts = {
    # decent sized media with audio+video, generally compatible with all platforms
    0: ["hasvid", "hasaud", "res:1440"],
    # sort preferring audio+video with the highest quality
    1: ["hasvid", "hasaud", "res"],
    # sort preferring audio+video with the lowest quality
    2: ["hasvid", "hasaud", "+res"],
    # sort preferring highest quality with priority on VP9 codec for platform compatibility
    3: ["codec:vp9", "hasvid", "res"],
    # sort preferring highest quality without concern for codec or audio
    4: ["hasvid", "res"],
}

pool_max = 10
pool = PoolCount()


routes = web.RouteTableDef()


@routes.view("/")
class YTDLProxy(web.View):
    async def head(self):
        if not self.request.query.get("url"):
            return web.Response(status=404)
        return await self.process()

    async def get(self):
        if not self.request.query.get("url"):
            return web.Response(status=404, text="Missing Url Param")
        return await self.process()

    async def process(self):
        url = await self.resolveUrl()
        if url: return web.Response(status=307, headers={"Location": url})
        else: return web.Response(status=408)

    async def resolveUrl(self):

        # silence the output of ytdl
        ytdl_opts = {"quiet": True}

        url = normalizeUrl(self.request.query.get("url"))
        mode = mode_map[self.request.query.get("m") or "0"]
        fid = self.request.query.get("f")
        host = urlparse(url).hostname
        # if format ID is provided, retrieve that explicitly
        if fid:
            ytdl_opts["format"] = fid
            cacheId = fid
            sort = None
        # otherwise use the "best" sorting based on the sort available
        else:
            # use either the given user sort, or extrapolate for the given preset mode
            s = self.request.query.get("s")
            if (s): sort = s.replace(" ", "").split(",")
            else: sort = list(sort_opts[mode])
            try: 
                if host.index("vimeo") > -1:
                    sort.append("proto:m3u8_native")
            except: pass
            ytdl_opts["format_sort"] = sort
            cacheId = ",".join(sort)

        _id = f"{cacheId}~{url}"
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
                print(f"Resolving '{cacheId}' for url: {url}")
                print("Cache hit")
                print(item.resolved_url)
                print(
                    f"{item.resolved_format} expires in {item.expiry - time.time()} seconds", flush=True
                )
                return item.resolved_url or ""

        cache_map[_id] = item = Item(url, sort)

        # wait for an pool slot to open
        timeout = time.time() + 30  # 30 seconds timelimit for waiting
        while pool.count >= pool_max:
            if time.time() > timeout: return None
            await sleep(1)
        print(ytdl_opts)
        with YoutubeDL(ytdl_opts) as ytdl:
            print(f"Resolving '{cacheId}' for url: {url}")
            print("Fetching fresh info", flush=True)
            pool.add()
            result = ytdl.extract_info(url, download=False)
            # print(result.keys())
            item.resolve(result)
            pool.remove()
            print(item.resolved_url)
            print(f"{item.resolved_format} expires in {item.expiry - time.time()} seconds", flush=True)

        print("")
        return item.resolved_url or ""


app = web.Application()
app.add_routes(routes)
print("Starting Qroxy server.")
web.run_app(app, host=config["server"]["host"], port=config["server"]["port"])
