import socket
import pytest
from fastapi import HTTPException
from utils import ssrf_ip_check
resolved_ip= [
    "127.0.0.1",
    "10.0.0.1",
    "172.16.0.1",
    "192.168.1.1",
    "169.254.169.254",
    "224.0.0.1",
    "0.0.0.0",
    "::1",
    "fc00::1",
    "fe80::1",
]
@pytest.mark.parametrize("resolved_ip",resolved_ip)
def test_ssrf_blocks_dns_resolving_to_private_ip(monkeypatch,resolved_ip,valid_url):
    def fake_getaddrinfo(host,port):
        return [
            (
                socket.AF_INET6 if ":" in resolved_ip else socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                (resolved_ip, port or 443),
            )
        ]
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        fake_getaddrinfo
    )
    url=valid_url.get("original_url")
   
    with pytest.raises(HTTPException) as exc:
        ssrf_ip_check(url)
    assert exc.value.status_code==400
    

   
    