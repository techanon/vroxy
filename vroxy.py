from __future__ import unicode_literals
import os
import logging as log
from aiohttp import web

from app.config import config
from app.middleware import makeTokenAuthzMiddleware
from app.resolver import resolveUrl
from app.exceptions import *

routes = web.RouteTableDef()
log.basicConfig(level=log.DEBUG)


@routes.view("/healthz")
class Health(web.View):
    async def get(self):
        return web.Response(status=200, text="OK")

@routes.view("/")
class YTDLProxy(web.View):
    async def head(self):
        log.debug('HEAD headers')
        log.debug(self.request.headers)
        if not self.request.query.get("url") and not self.request.query.get("u"):
            res = web.Response(status=404)
            return res
        return await self.process()

    async def get(self):
        log.debug('GET headers')
        log.debug(self.request.headers)
        if not self.request.query.get("url") and not self.request.query.get("u"):
            res = web.Response(status=404, text="Missing Url Param")
            return res
        return await self.process()

    async def process(self):
        url = None
        res = web.Response(status=500)
        try:
            url = await resolveUrl(self.request.query)
            res = web.Response(status=307, headers={"Location": url})
        except Error400BadRequest:
            res = web.Response(status=400)
        except Error403Forbidden:
            res = web.Response(status=403)
        except Error403Whitelist:
            res = web.Response(status=403, text="Domain not in whitelist")
        except Error404NotFound:
            res = web.Response(status=404)
        except Error408Timeout:
            res = web.Response(status=408)
        except Error410Gone:
            res = web.Response(status=410)
        except Error429TooManyRequests:
            res = web.Response(status=429)
        except Exception:
            res = web.Response(status=500)
        return res


async def strip_headers(req: web.Request, res: web.StreamResponse):
    del res.headers['Server']

app = web.Application()
if auth_tokens_config := config["server"].get("auth_tokens"):
    auth_tokens = [t.strip() for t in auth_tokens_config.split(",")]
    authz_middleware = makeTokenAuthzMiddleware(auth_tokens)
    app.middlewares.append(authz_middleware)

app.add_routes(routes)
app.on_response_prepare.append(strip_headers)
print("Starting Vroxy server.")
if os.environ.get("TMUX"):
    print("--- TMUX USAGE REMINDER ---")
    print("If the service is running in a TMUX instance, you can exit without killing the service with CTRL+B and then press D")
    print("If you run the CTRL+C command, you will kill the service making your urls return 502.")
    print(f"Remember you can restart the service by exiting the TMUX instance with CTRL+B and then D, then run 'bash {os.path.dirname(__file__)}/vroxy_reload.sh'", flush=True)
web.run_app(app, host=config["server"]["host"], port=config["server"]["port"])
