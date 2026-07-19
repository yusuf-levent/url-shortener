import hashlib
from config import settings
from fastapi import Request,HTTPException,status
import ipaddress
import socket
from urllib.parse import urlparse
from loguru import logger
def hash_email(plain_email:str)->str:
    valid_email=plain_email.strip().lower()
    return hashlib.sha256(valid_email.encode()).hexdigest()

def get_ip_hash(request:Request)->str:
    cf_ip = request.headers.get("CF-Connecting-IP")
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    x_real_ip = request.headers.get("X-Real-IP")
    
    if cf_ip:
        ip_address= cf_ip
    elif x_forwarded_for:
        ip_address= x_forwarded_for.split(",")[0].strip()
    elif x_real_ip:
        ip_address= x_real_ip
    else:
        ip_address=request.client.host
    if ip_address=="unknown":
        return "unknown"
    return hashlib.sha256(f"{ip_address}{settings.SECRET_KEY}".encode()).hexdigest()


def ssrf_ip_check(url_str):
    # Parse the URL and extract components such as scheme, hostname, and port.
    parsed_url=urlparse(url_str)
    if parsed_url.scheme not in ["http","https"]:
        logger.warning("Url is not http or https")
        #only accept these  protocols
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The provided URL is invalid or not reachable."
            )
    
    host=parsed_url.hostname 
    # Extract the hostname (e.g. example.com or 192.168.1.1).

    if not host:
        logger.warning("Host not found in url")
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The provided URL is invalid or not reachable."
            )
    
    try:
        port=parsed_url.port
        infos=socket.getaddrinfo(host,port)
        # Resolve the hostname to all available IPv4 and IPv6 addresses.
    except (socket.gaierror,ValueError):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The provided URL is invalid or not reachable."
        )


    for info in infos:
        ip_address_str=info[4][0]
         # Extract the resolved IP address from the socket address.
        ip_address=ipaddress.ip_address(ip_address_str)
         # Convert the IP string into an ipaddress object for validation.

        if (ip_address.is_loopback # Reject localhost addresses.
        or ip_address.is_private # Reject private network addresses.
        or ip_address.is_link_local # Reject link-local addresses.
        or  ip_address.is_multicast # Reject multicast addresses.
        or ip_address.is_reserved # Reject reserved IP addresses.
        or ip_address.is_unspecified):
            logger.warning("IP address in url is (localhost | private | link-local | multicast | reserved | unspecified)")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The provided URL is invalid or not reachable."
            )
        
    return True