import subprocess
import re

def scan_printer(ip_address: str):
    """
    Scans a printer via SNMP using system `snmpget`.
    Tries to fetch sysDescr and sysName.
    """
    community = 'public'
    # sysDescr, sysName, sysLocation OIDs
    oids = [
        '1.3.6.1.2.1.1.1.0', # sysDescr
        '1.3.6.1.2.1.1.5.0', # sysName
        '1.3.6.1.2.1.1.6.0'  # sysLocation
    ]
    
    result = {
        "model": None,
        "status": "Unknown",
        "location": "Unknown",
        "sys_description": None,
        "sys_location": None,
        "sys_name": None
    }

    try:
        # Construct command: snmpget -v2c -c public -Oqv <IP> <OID1> <OID2> <OID3>
        cmd = ['snmpget', '-v2c', '-c', community, '-Oqv', ip_address] + oids
        
        # Timeout 4 seconds
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=4)
        
        if process.returncode == 0:
            lines = process.stdout.strip().split('\n')
            if len(lines) >= 1:
                result["sys_description"] = lines[0].strip('"')
                result["model"] = result["sys_description"]
                result["status"] = "Ready"
            
            if len(lines) >= 2:
                result["sys_name"] = lines[1].strip('"')
            
            if len(lines) >= 3:
                result["sys_location"] = lines[2].strip('"')
                result["location"] = result["sys_location"]
        else:
            print(f"SNMP failed for {ip_address}: {process.stderr}")

    except Exception as e:
        print(f"SNMP error: {e}")

    return result
