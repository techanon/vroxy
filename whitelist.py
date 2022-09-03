from pathlib import Path
from typing import List, NamedTuple

import tldextract


class WhitelistedDomain(NamedTuple):
    """union of tldextract's ExtractResult."""

    subdomain: str
    registered_domain: str

    def matches(self, url: str) -> bool:
        parsed = tldextract.extract(url)
        if self.subdomain != "*" and self.subdomain != parsed.subdomain:
            return False
        return self.registered_domain == parsed.registered_domain


class DomainWhitelist:
    whitelist: List[WhitelistedDomain]

    def __init__(self, whitelist: List[WhitelistedDomain]):
        self.whitelist = whitelist

    def allows(self, url: str) -> bool:
        for d in self.whitelist:
            if d.matches(url):
                return True
        return False


def load_list(path: str) -> DomainWhitelist:
    wl = []
    with open(path, "r") as f:
        for line in f:
            wl.append(line)

    wl = [tldextract.extract(d) for d in wl]
    return DomainWhitelist(
        [
            WhitelistedDomain(
                subdomain=d.subdomain, registered_domain=d.registered_domain
            )
            for d in wl
        ]
    )
