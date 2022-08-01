from urllib.parse import urlparse, urlencode, urlunparse, parse_qs


def normalizeUrl(url) -> str:
    # parse for domain, and handle per domain
    url_parts = urlparse(url)

    if url_parts.hostname in ["youtube.com", "youtu.be", "www.youtube.com"]:
        return normalizeYT(url_parts)

    return urlunparse(url_parts)


def normalizeYT(url_parts) -> str:
    # remove the list query param as it causes excess delay in loading information
    url_query = parse_qs(url_parts.query)
    new_query = ""
    if "v" in url_query:
        new_query = f"v={url_query['v'][0]}"
    url_parts = url_parts._replace(query=new_query)
    return urlunparse(url_parts)


def normalizeVimeo(url_parts) -> str:
    return urlunparse(url_parts)


def normalizeTwitch(url_parts) -> str:
    return urlunparse(url_parts)
