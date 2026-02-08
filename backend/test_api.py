from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_create_printer():
    # Cleanup before test if possible, or use fresh db fixture. 
    # For now, simplistic test.
    printer_data = {"name": "Test Printer", "ip_address": "192.168.1.100", "model": "HP LaserJet", "location": "Office 1"}
    response = client.post("/printers/", json=printer_data)
    if response.status_code == 400: # Already exists?
        assert response.json()["detail"] == "Printer with this IP already exists"
    else:
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Printer"
        assert "id" in data

def test_read_printers():
    response = client.get("/printers/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_update_status():
    # First create or get a printer
    response = client.get("/printers/")
    data = response.json()
    if not data:
        printer_data = {"name": "Update Test", "ip_address": "10.0.0.1", "model": "Canon", "location": "Lab"}
        create_res = client.post("/printers/", json=printer_data)
        printer_id = create_res.json()["id"]
    else:
        printer_id = data[0]["id"]
    
    response = client.put(f"/printers/{printer_id}", json={"status": "Online"})
    assert response.status_code == 200
    assert response.json()["status"] == "Online"

def test_scan_printer():
    # Ensure a printer exists
    response = client.get("/printers/")
    data = response.json()
    if not data:
        printer_data = {"name": "Scan Test", "ip_address": "10.0.0.2", "model": "Unknown", "location": "Unknown"}
        create_res = client.post("/printers/", json=printer_data)
        printer_id = create_res.json()["id"]
    else:
        printer_id = data[0]["id"]

    # Test SNMP scan
    response = client.post(f"/printers/{printer_id}/scan?protocol=snmp")
    assert response.status_code == 200
    data = response.json()
    assert "SNMP" in data["model"] or "SNMP" in data["location"]
    
    # Test Web scan
    response = client.post(f"/printers/{printer_id}/scan?protocol=web")
    assert response.status_code == 200
    data = response.json()
    assert "Web" in data["model"] or "Web" in data["location"]
