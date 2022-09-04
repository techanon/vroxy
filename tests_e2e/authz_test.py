import re
import requests

def test_authz_token():
    msg = "Missing authorization token"
    r = requests.get('http://vroxy_e2e_authz:8008/healthz')
    assert r.status_code == 401
    assert r.text == msg
    r = requests.get('http://vroxy_e2e_authz:8008/healthz?token=abc')
    assert r.status_code == 200
    assert r.text == "OK"
    r = requests.get('http://vroxy_e2e_authz:8008/healthz?token=123')
    assert r.status_code == 200
    assert r.text == "OK"
    r = requests.get('http://vroxy_e2e_authz:8008/healthz?token=bogus')
    assert r.status_code == 401
    assert r.text == msg
    r = requests.get('http://vroxy_e2e_authz:8008/healthz', headers={"Authorization": "Bearer abc"})
    assert r.status_code == 200
    assert r.text == "OK"
    r = requests.get('http://vroxy_e2e_authz:8008/healthz', headers={"Authorization": "Bearer 123"})
    assert r.status_code == 200
    assert r.text == "OK"
    r = requests.get('http://vroxy_e2e_authz:8008/healthz', headers={"Authorization": "Bearer bogus"})
    assert r.status_code == 401
    assert r.text == msg
    r = requests.get('http://vroxy_e2e_authz:8008/healthz', headers={"Authorization": "bogus"})
    assert r.status_code == 401
    assert r.text == msg

