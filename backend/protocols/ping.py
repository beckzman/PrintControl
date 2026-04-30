import subprocess
import platform
import asyncio

def ping_host(ip_address: str) -> bool:
    """
    Pings a host to check if it's online.
    Returns True if reachable, False otherwise.
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip_address]
    
    try:
        # Timeout after 2 seconds to avoid hanging
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2, check=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False

async def ping_host_async(ip_address: str) -> bool:
    """
    Async version of ping_host to avoid blocking the event loop.
    """
    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, ping_host, ip_address)
    except Exception:
        return False
