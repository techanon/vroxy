from whitelist import load_list, WhitelistedDomain, _parse_line


def test_whitelisted_domain():
    wildcard = WhitelistedDomain(
        subdomain="*", registered_domain="youtube.com", fqdn="*.youtube.com"
    )
    assert wildcard.matches("https://www.youtube.com/watch?v=aIEYKaRHiDM")
    assert wildcard.matches("https://youtube.com/watch?v=aIEYKaRHiDM")
    reg_domain = WhitelistedDomain(
        subdomain="", registered_domain="youtube.com", fqdn="youtube.com"
    )
    assert not reg_domain.matches("https://www.youtube.com/watch?v=aIEYKaRHiDM")
    assert reg_domain.matches("https://youtube.com/watch?v=aIEYKaRHiDM")
    sub_domain = WhitelistedDomain(
        subdomain="s1", registered_domain="youtube.com", fqdn="s1.youtube.com"
    )
    assert not sub_domain.matches("https://www.youtube.com/watch?v=aIEYKaRHiDM")
    assert not sub_domain.matches("https://youtube.com/watch?v=aIEYKaRHiDM")
    assert sub_domain.matches("https://s1.youtube.com/watch?v=aIEYKaRHiDM")


def test_line_parsing():
    assert _parse_line("") == ""
    assert _parse_line("\n") == ""
    assert _parse_line("# comment") == ""
    assert _parse_line("#########") == ""
    assert _parse_line("     domain.com   ") == "domain.com"
    assert _parse_line("domain.com # comment") == "domain.com"
    assert _parse_line("domain.com#comment") == "domain.com"
    assert _parse_line("# domain.com #comment") == ""


def test_file_parsing():
    expected_domains = {
        "domain1.com",
        "domain2.com",
        "sub.domain3.com",
        "*.domain4.com",
        "domain5.com",
    }
    wl = load_list("tests/whitelist-example.txt")
    print(wl.whitelist)
    assert wl.patterns == expected_domains


def test_load_list():
    wl = load_list("config/vrchat-whitelist.txt")
    assert not wl.allows("https://totally.bogus.test/yep")
    assert wl.allows("https://www.youtube.com/watch?v=aIEYKaRHiDM")
    assert wl.allows("https://youtube.com/watch?v=aIEYKaRHiDM")
    assert wl.allows("https://youtu.be/aIEYKaRHiDM")
    assert wl.allows("www.youtube.com/watch?v=aIEYKaRHiDM")
    assert wl.allows("youtube.com/watch?v=aIEYKaRHiDM")
    assert wl.allows("youtu.be/aIEYKaRHiDM")
    assert wl.allows("soundcloud.com/bogus")
    assert wl.allows("drive.google.com/bogus")
    assert not wl.allows("google.com/bogus")
    assert wl.allows("facebook.com/bogus")
    assert wl.allows("nicovideo.jp/bogus")
    assert wl.allows("something.nicovideo.jp/bogus")
    assert wl.allows("vimeo.com/bogus")
    assert wl.allows("something.vimeo.com/bogus")
    assert wl.allows("youku.com/bogus")
    assert wl.allows("something.youku.com/bogus")
    assert wl.allows("mixcloud.com/bogus")
    assert not wl.allows("something.mixcloud.com/bogus")
    assert wl.allows("something.vrcdn.live")
    assert wl.allows("something.vrcdn.video")
    assert wl.allows("https://streamable.com/o/hn8hq")
