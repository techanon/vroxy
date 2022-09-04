import hmac
from typing import List
from aiohttp.web import middleware, Response


def makeTokenAuthzMiddleware(tokens: List[str]):
    """Authorizes requests based on a static list of bearer tokens"""

    @middleware
    async def _tokenAuthzMiddleware(request, handler):
        auth_token = ""
        # Authorization: Bearer <token>
        if auth_header := request.headers.get("Authorization"):
            header_parts: str = auth_header.split(None, 1)
            if len(header_parts) == 2 and header_parts[0].lower() == "bearer":
                auth_token = header_parts[1]
        # Technically accepting tokens in a query param is an antipattern. It
        # can lead to leaking tokens in request logs and such. This is an
        # acceptable risk. We are mostly just trying to prevent the wide public
        # internet from making a ton of requests. Some usecases for vroxy might
        # not support sending headers.
        if auth_query := request.query.get("token"):
            auth_token = auth_query
        for t in tokens:
            # compare_digest to avoid timing attacks
            if hmac.compare_digest(t, auth_token):
                return await handler(request)

        return Response(status=401, text="Missing authorization token")

    return _tokenAuthzMiddleware
