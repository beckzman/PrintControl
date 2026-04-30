from sqlalchemy.orm import Session
import crud, schemas
from protocols import snmp, web, ping
import asyncio

def update_printer_status(db: Session, printer_id: int, forced_protocol: str = None):
    """
    Unified function to scan a printer using all enabled probes.
    If forced_protocol is provided, it prioritizes and focuses on that specific probe.
    """
    db_printer = crud.get_printer(db, printer_id=printer_id)
    if not db_printer:
        return None
    
    enabled_probes = ["ping"] # Default if no type assigned
    discovery_config = {}
    
    if db_printer.printer_type:
        enabled_probes = db_printer.printer_type.probes or []
        if db_printer.printer_type.discovery_config:
            discovery_config = db_printer.printer_type.discovery_config

    results = {
        "status": db_printer.status, # Keep current if possible
        "model": db_printer.model,
        "location": db_printer.location
    }
    
    is_online = True
    
    # If a specific protocol is forced, we might bypass the general ping/enabled check logic
    probes_to_run = [forced_protocol] if forced_protocol else enabled_probes

    # 1. Check Ping if it's in the list and NOT bypassed by a specific forced high-level probe
    # However, for a generic update, we usually want ping first.
    if "ping" in probes_to_run:
        is_online = ping.ping_host(db_printer.ip_address)
        if not is_online and not forced_protocol:
            results["status"] = "Offline"
            return crud.update_printer(db, printer_id, schemas.PrinterUpdate(**results))
        elif is_online:
            results["status"] = "Online"

    # 2. Run other probes
    probe_success = False
    last_protocol = "Ping" if is_online else None
    
    if "snmp" in probes_to_run:
        try:
            snmp_data = snmp.scan_printer(db_printer.ip_address)
            if snmp_data and snmp_data.get("status") != "Unknown":
                results["status"] = snmp_data.get("status")
                results["model"] = snmp_data.get("model") or results["model"]
                results["location"] = snmp_data.get("location") or results["location"]
                results["sys_location"] = snmp_data.get("sys_location")
                results["sys_description"] = snmp_data.get("sys_description")
                probe_success = True
                last_protocol = "SNMP"
        except Exception as e:
            print(f"SNMP Probe failed for {db_printer.ip_address}: {e}")

    if "web" in probes_to_run:
        try:
            web_data = web.scan_printer(db_printer.ip_address, config=discovery_config)
            if web_data and web_data.get("status") != "Unknown":
                results["status"] = web_data.get("status")
                results["model"] = web_data.get("model") or results["model"]
                results["location"] = web_data.get("location") or results["location"]
                probe_success = True
                last_protocol = "Web"
                
                # Save web crawl content
                if web_data.get("html_content"):
                    crud.save_web_crawl(db, printer_id, web_data["html_content"])
        except Exception as e:
            print(f"Web Probe failed for {db_printer.ip_address}: {e}")

    # Fallback status refinement
    if not probe_success and is_online:
        results["status"] = "Online"
        last_protocol = "Ping"
    elif not is_online and not probe_success and not forced_protocol:
        results["status"] = "Offline"
        last_protocol = None

    results["last_protocol"] = last_protocol

    updated_printer = crud.update_printer(db, printer_id, schemas.PrinterUpdate(**results))
    return updated_printer, (probe_success or (is_online if forced_protocol == 'ping' else False) if forced_protocol else probe_success or is_online)

async def update_printer_status_async(db: Session, printer_id: int, forced_protocol: str = None):
    """
    Async version of update_printer_status to avoid blocking the event loop.
    Uses asyncio.gather to run probes concurrently where possible.
    """
    db_printer = crud.get_printer(db, printer_id=printer_id)
    if not db_printer:
        return None, False
    
    enabled_probes = ["ping"]
    discovery_config = {}
    
    if db_printer.printer_type:
        enabled_probes = db_printer.printer_type.probes or []
        if db_printer.printer_type.discovery_config:
            discovery_config = db_printer.printer_type.discovery_config

    results = {
        "status": db_printer.status,
        "model": db_printer.model,
        "location": db_printer.location
    }
    
    is_online = True
    probes_to_run = [forced_protocol] if forced_protocol else enabled_probes

    # 1. Check Ping first (must complete before other probes)
    if "ping" in probes_to_run:
        is_online = await ping.ping_host_async(db_printer.ip_address)
        if not is_online and not forced_protocol:
            results["status"] = "Offline"
            updated_printer = crud.update_printer(db, printer_id, schemas.PrinterUpdate(**results))
            return updated_printer, False
        elif is_online:
            results["status"] = "Online"

    # 2. Run SNMP and Web probes concurrently
    probe_success = False
    last_protocol = "Ping" if is_online else None
    snmp_done = False
    web_done = False
    
    tasks = []
    if "snmp" in probes_to_run:
        tasks.append(("snmp", snmp.scan_printer_async(db_printer.ip_address)))
    if "web" in probes_to_run:
        tasks.append(("web", web.scan_printer_async(db_printer.ip_address, config=discovery_config)))
    
    if tasks:
        completed = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
        
        for i, result in enumerate(completed):
            probe_name = tasks[i][0]
            
            if isinstance(result, Exception):
                print(f"{probe_name.upper()} Probe failed for {db_printer.ip_address}: {result}")
                continue
            
            if probe_name == "snmp" and result and result.get("status") != "Unknown":
                results["status"] = result.get("status")
                results["model"] = result.get("model") or results["model"]
                results["location"] = result.get("location") or results["location"]
                results["sys_location"] = result.get("sys_location")
                results["sys_description"] = result.get("sys_description")
                probe_success = True
                last_protocol = "SNMP"
                snmp_done = True
                
            elif probe_name == "web" and result and result.get("status") != "Unknown":
                results["status"] = result.get("status")
                results["model"] = result.get("model") or results["model"]
                results["location"] = result.get("location") or results["location"]
                probe_success = True
                last_protocol = "Web"
                web_done = True
                
                # Save web crawl content
                if result.get("html_content"):
                    crud.save_web_crawl(db, printer_id, result["html_content"])

    # Fallback status refinement
    if not probe_success and is_online:
        results["status"] = "Online"
        last_protocol = "Ping"
    elif not is_online and not probe_success and not forced_protocol:
        results["status"] = "Offline"
        last_protocol = None

    results["last_protocol"] = last_protocol

    updated_printer = crud.update_printer(db, printer_id, schemas.PrinterUpdate(**results))
    success = probe_success or (is_online if forced_protocol == 'ping' else False) if forced_protocol else probe_success or is_online
    return updated_printer, success
