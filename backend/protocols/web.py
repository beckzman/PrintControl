import requests
from bs4 import BeautifulSoup
import re

def scan_printer(ip_address: str, config: dict = None):
    """
    Scans a printer via HTTP with improved detection logic for HP and other brands.
    """
    # Common paths to check for metadata
    paths = [
        "/", 
        "/index.html", 
        "/home.html",
        "/config.html", 
        "/status.html", 
        "/DevMgmt/ProductConfigDyn.xml", 
        "/hp/device/this.LCDispatcher"
    ]
    result = {
        "model": None,
        "status": "Online",
        "location": "Unknown"
    }
    
    for path in paths:
        url = f"http://{ip_address}{path}"
        try:
            # Use a generic User-Agent to avoid being blocked, allow redirects, and skip SSL verification
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
            response = requests.get(url, timeout=4, headers=headers, allow_redirects=True, verify=False)
            if response.status_code != 200:
                continue
            
            # 1. Check title/meta tags
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else ""
            if title and len(title) > 3 and "Home" not in title and "Loading" not in title:
                result["model"] = title.strip()
                break

            # 2. Check for HP redirects or specific content patterns
            text_preview = response.text[:2000] # Use a preview for safety
            
            # Heuristic: HP EWS usually has "top.location.href" or "hp/device"
            if "top.location.href" in text_preview and "/#/index.html" in text_preview:
                # If we're at the root, we know it's an HP, but we need the model.
                # Often the DeviceDescription is in /DevMgmt/ProductConfigDyn.xml
                continue # Try next path like ProductConfigDyn.xml
            
            # 3. Regex search for model-like strings
            # Look for HP ENVY, LaserJet, OfficeJet, Color LaserJet, etc.
            # Also catch things like "Canon MG3600"
            patterns = [
                (r"(HP\s+[A-Za-z0-9]+\s+[0-9]+)", None),
                (r"(LaserJet\s+[A-Za-z0-9]+)", "HP"),
                (r"(OfficeJet\s+[A-Za-z0-9]+)", "HP"),
                (r"(ENVY\s+[0-9]+)", "HP"),
                (r"(Canon\s+[A-Z0-9]+)", None),
                (r"(Kyocera\s+[A-Za-z0-9\-]+)", None),
                (r"(Printronix\s+[A-Za-z0-9]+)", None),
                (r"(PrintNet)", "Printronix")
            ]
            for pattern, vendor in patterns:
                match = re.search(pattern, text_preview, re.IGNORECASE)
                if match:
                    model_found = match.group(1).strip()
                    if vendor and vendor not in model_found:
                         result["model"] = f"{vendor} {model_found}"
                    else:
                         result["model"] = model_found
                    break
            
            if result.get("model"):
                break

        except Exception as e:
            # print(f"Web scan debug for {url}: {e}") # Suppress noise
            continue

    # Fallback: If still unknown but online, use a generic descriptive model
    if not result.get("model"):
        result["model"] = "Unknown Printer (Web available)"
    
    return result
