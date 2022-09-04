from __future__ import unicode_literals
import time
import re
import random
import multidict
import logging as log

from asyncio import sleep
from typing import Optional
from urllib.parse import urlparse
from yt_dlp import YoutubeDL

from app.config import config
from app.exceptions import *
from app.normalize import normalizeUrl
from app.whitelist import DomainWhitelist, load_list

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
sort_opts = {
    # decent sized media with audio+video, generally compatible with all platforms
    0: ["proto:https", "hasvid", "hasaud", "res:1440"],
    # sort preferring audio+video with the highest quality
    1: ["hasvid", "hasaud", "res"],
    # sort preferring audio+video with the lowest quality
    2: ["hasvid", "hasaud", "+res"],
    # sort preferring highest quality with priority on VP9 codec for platform compatibility
    3: ["codec:vp9", "hasvid", "res"],
    # sort preferring highest quality without concern for codec or audio
    4: ["hasvid", "res"],
}
expire_regex = re.compile(r"exp(?:ir(?:es?|ation))?=(\d+)")
nextGCTime = time.time() + 3600
cache_map = {}
domain_whitelist: Optional[DomainWhitelist] = None

if wl_path := config["server"]["whitelist"]:
    domain_whitelist = load_list(wl_path)


class Item:
    def __init__(self, url, sort):
        self.original_url = url
        self.hostname = urlparse(url).hostname
        self.resolved_url = None
        self.resolved_id = None
        self.resolved_format = None
        self.sort = sort
        self.expiry = 0
        self.lastAccess = 0
        self.processing = True

    def resolve(self, f) -> None:
        if self.sort:
            f = f["formats"][-1]
        self.resolved_url = f["url"]
        self.resolved_id = f["format_id"]
        self.resolved_format = f["format"]
        self.expiry = self.extractExpiry()
        self.processing = False

    def extractExpiry(self) -> float:
        # default to 10s for m3u8 links as they will force an improper starting time if the cache is used for too long
        # allows 10s for handling a burst of users requesting the same URL (ie: someone just queued a new vid)
        # if ".m3u8" in self.resolved_url:
        #     return time.time() + 10
        p = expire_regex.search(self.resolved_url)
        if p is not None:
            return int(p.group(1))
        return time.time() + 600  # default to 10 minute


class PoolCount:
    def __init__(self):
        self.count = 0

    def add(self):
        self.count += 1

    def remove(self):
        self.count -= 1


pool_max = config.get("ytdl", "pool_size", fallback=10)
pool = PoolCount()


async def resolveUrl(query: multidict.MultiDictProxy[str]) -> str:
    rid = random.getrandbits(16)
    global nextGCTime
    curTime = time.time()
    # clean up the cache every hour
    if curTime > nextGCTime:
        nextGCTime = time.time() + 3600
        purge = []
        for cache_id, cache_item in cache_map.items():
            # if the item is expired or was last accessed over an hour ago, purge
            if cache_item.lastAccess + 3600 < curTime or cache_item.expiry < curTime:
                purge.append(cache_id)
        for purge_id in purge:
            del cache_map[purge_id]

    # silence the output of ytdl
    ytdl_opts = {"quiet": True}

    url = normalizeUrl(query.get("url") or query.get("u"))

    if domain_whitelist and not domain_whitelist.allows(url):
        raise Error403Whitelist

    mode = mode_map[query.get("m") or "0"]
    fid = query.get("f")
    host = urlparse(url).hostname
    # if format ID is provided, retrieve that explicitly
    if fid:
        ytdl_opts["format"] = fid
        cacheId = fid
        sort = None
    # otherwise use the "best" sorting based on the sort available
    else:
        # use either the given user sort, or extrapolate for the given preset mode
        s = query.get("s")
        if s:
            sort = s.replace(" ", "").split(",")
        else:
            sort = list(sort_opts[mode])
        try:
            if host.index("vimeo") > -1:
                sort.append("proto:m3u8_native")
        except:
            pass
        ytdl_opts["format_sort"] = sort
        cacheId = ",".join(sort)

    _id = f"{cacheId}~{url}"
    if _id in cache_map:
        item = cache_map[_id]
        if item.expiry < curTime:
            log.debug(f"[{rid}] Cache expired")
            del cache_map[_id]
        else:
            # wait until the other request for the same url resolves,
            # then use the cached url from that
            while item.processing:
                await sleep(1)
            log.info(f"[{rid}] Resolving '{cacheId}' for url: {url}")
            log.info(f"[{rid}] Cache hit. Using cached url.")
            log.debug(f"[{rid}] {item.resolved_url}")
            print(
                f"[{rid}] {item.resolved_format} expires in {item.expiry - curTime} seconds"
            )
            item.lastAccess = curTime
            return item.resolved_url or ""

    cache_map[_id] = item = Item(url, sort)

    # wait for an pool slot to open
    timeout = curTime + 30  # 30 seconds timelimit for waiting
    while pool.count >= pool_max:
        if curTime > timeout:
            log.info(f"[{rid}] Request timed out waiting for pool slot ({pool.count})")
            return None
        await sleep(1)
    with YoutubeDL(ytdl_opts) as ytdl:
        log.info(f"[{rid}] Resolving '{cacheId}' for url: {url}")
        log.info(f"[{rid}] Fetching fresh info")
        pool.add()
        try:
            result = ytdl.extract_info(url, download=False)
        except ytdl.utils.DownloadError as e:
            print(str(e))
            raise Error400BadRequest
        # except ytdl.utils.ContentTooShortError:
        #     pass
        # except ytdl.utils.ExtractorError:
        #     pass
        # except ytdl.utils.GeoRestrictedError:
        #     pass
        # except ytdl.utils.PostProcessingError:
        #     pass
        # except ytdl.utils.SameFileError:
        #     pass
        # except ytdl.utils.UnavailableVideoError:
        #     pass
        except Exception as e:
            log.debug("Unexpected error happened with YTDL")
            log.debug(str(e))
            raise
        # print(result.keys())
        item.resolve(result)
        pool.remove()
        log.debug(f"[{rid}] {item.resolved_url}")
        log.info(
            f"[{rid}] {item.resolved_format} expires in {item.expiry - curTime} seconds"
        )

    item.lastAccess = curTime
    return item.resolved_url or ""
