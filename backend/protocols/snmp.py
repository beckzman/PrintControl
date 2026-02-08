import subprocess
import re

def scan_printer(ip_address: str):
    """
    Scans a printer via SNMP using system `snmpget`.
    Tries to fetch sysDescr and sysName.
    """
    community = 'public'
    # sysDescr and sysName OIDs
    oids = ['1.3.6.1.2.1.1.1.0', '1.3.6.1.2.1.1.5.0']
    
    result = {
        "model": None,
        "status": "Unknown",
        "location": "Unknown"
    }

    try:
        # Construct command: snmpget -v2c -c public -Oqv <IP> <OID1> <OID2>
        # -Oqv: Output value only, quick print
        cmd = ['snmpget', '-v2c', '-c', community, '-Oqv', ip_address] + oids
        
        # Timeout 3 seconds
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        
        if process.returncode == 0:
            lines = process.stdout.strip().split('\n')
            if len(lines) >= 1:
                # sysDescr usually contains the model
                sys_descr = lines[0].strip('"')
                # Simple heuristic to extract model if it's verbose
                # E.g. "HP ETHERNET MULTI-ENVIRONMENT,ROM A.21.00,JETDIRECT,JD128,EEPROM V.28.23,CIDATE 06/07/2001"
                # But often it's "HP LaserJet 4000 Series"
                result["model"] = sys_descr 
                result["status"] = "Ready" # If we got a response, it's ready-ish
            
            if len(lines) >= 2:
                sys_name = lines[1].strip('"')
                # Could be used for hostname/location logic
                pass
                
        else:
            print(f"SNMP failed for {ip_address}: {process.stderr}")

    except Exception as e:
        print(f"SNMP error: {e}")

    return result
