import socket

def resolve_hostname(hostname: str) -> str:
    """
    Resolves a hostname to an IP address.
    Returns the IP address if successful, or None if failed.
    """
    try:
        # Get the first IP address associated with the hostname
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None

def reverse_resolve(ip_address: str) -> str:
    """
    Resolves an IP address to a hostname.
    Returns the hostname if successful, or None if failed.
    """
    try:
        # Returns (hostname, aliaslist, ipaddrlist)
        return socket.gethostbyaddr(ip_address)[0]
    except (socket.herror, socket.gaierror):
        return None
