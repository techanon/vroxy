from typing import List, NamedTuple, Set

import tldextract


class WhitelistedDomain(NamedTuple):
    """union of tldextract's ExtractResult."""

    fqdn: str
    registered_domain: str
    subdomain: str

    def matches(self, url: str) -> bool:
        parsed = tldextract.extract(url)
        if self.subdomain != "*" and self.subdomain != parsed.subdomain:
            return False
        return self.registered_domain == parsed.registered_domain


class DomainWhitelist:
    whitelist: List[WhitelistedDomain]

    def __init__(self, whitelist: List[WhitelistedDomain]):
        self.whitelist = whitelist

    @property
    def patterns(self) -> Set[str]:
        return {d.fqdn for d in self.whitelist}

    def allows(self, url: str) -> bool:
        for d in self.whitelist:
            if d.matches(url):
                return True
        return False


def _parse_line(line: str) -> str:
    line = line.strip()
    if not line:
        return ""
    if "#" in line:
        return _parse_line(line.split("#")[0])
    return line


def load_list(path: str) -> DomainWhitelist:
    wl = []
    with open(path, "r") as f:
        for line in f:
            if pattern := _parse_line(line):
                wl.append(pattern)

    wl = [tldextract.extract(d) for d in wl]
    return DomainWhitelist(
        [
            WhitelistedDomain(
                fqdn=d.fqdn,
                registered_domain=d.registered_domain,
                subdomain=d.subdomain,
            )
            for d in wl
        ]
    )
