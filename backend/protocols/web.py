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
        "/ioPortStatus.html",
        "/DevMgmt/ProductConfigDyn.xml", 
        "/hp/device/this.LCDispatcher"
    ]
    result = {
        "model": None,
        "status": "Online",
        "location": "Unknown"
    }
    
    all_contents = []
    
    for path in paths:
        url = f"http://{ip_address}{path}"
        try:
            # Use a generic User-Agent to avoid being blocked, allow redirects, and skip SSL verification
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
            response = requests.get(url, timeout=4, headers=headers, allow_redirects=True, verify=False)
            if response.status_code != 200:
                continue
            
            # Label and aggregate content
            content_marker = f"\n{'='*20} URL: {path} {'='*20}\n"
            all_contents.append(content_marker + response.text)
            
            # 1. Check title/meta tags (only if model not found yet)
            if not result.get("model"):
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.string if soup.title else ""
                if title and len(title) > 3 and "Home" not in title and "Loading" not in title:
                    result["model"] = title.strip()

            # 2. Check for HP redirects or specific content patterns
            # Note: We continue loop to get ALL pages even if model found
            text_preview = response.text[:2000] # Use a preview for safety
            
            # 3. Regex search for model-like strings (only if model not found yet)
            if not result.get("model"):
                patterns = [
                    (r"(HP\s+[A-Za-z0-9]+\s+[0-9]+)", None),
                    (r"(LaserJet\s+[A-Za-z0-9]+)", "HP"),
                    (r"(OfficeJet\s+[A-Za-z0-9]+)", "HP"),
                    (r"(ENVY\s+[0-9]+)", "HP"),
                    (r"(Canon\s+[A-Z0-9]+)", None),
                    (r"(Kyocera\s+[A-Za-z0-9\-]+)", None),
                    (r"(Printronix\s+[A-Za-z0-9]+)", None),
                    (r"(T8 [0-9]+)", "Printronix"),
                    (r"(P8 [0-9]+)", "Printronix"),
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

        except Exception as e:
            # print(f"Web scan debug for {url}: {e}") # Suppress noise
            continue

    # Set consolidated content
    if all_contents:
        result["html_content"] = "".join(all_contents)

    # Fallback: If still unknown but we reached it, use a generic descriptive model
    if not result.get("model") and result.get("html_content"):
        result["model"] = "Unknown Printer (Web available)"
    
    return result
