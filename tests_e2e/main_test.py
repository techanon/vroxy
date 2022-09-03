import re
import requests

def test_healthcheck():
    r = requests.get('http://vroxy_e2e:8008/healthz')
    assert r.status_code == 200
    assert r.text == "OK"

def test_url_resolve():
    r = requests.get('http://vroxy_e2e:8008/?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DdQw4w9WgXcQ', allow_redirects=False)
    assert r.status_code == 307
    assert re.match(r'https://.+googlevideo\.com/.+', r.headers["Location"])

