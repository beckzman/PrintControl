import requests

API_URL = "http://localhost:8001"

def test_master_data():
    # 1. Create Vendor
    vendor_data = {"name": "TestVendorHP"}
    response = requests.post(f"{API_URL}/vendors/", json=vendor_data)
    if response.status_code == 200:
        print("Vendor created successfully:", response.json())
        vendor_id = response.json()["id"]
    elif response.status_code == 400 and "already exists" in response.text:
        print("Vendor already exists, fetching...")
        # Get vendor ID (mock retrieval since we don't have get_by_name exposed directly in URL, but listing works)
        response = requests.get(f"{API_URL}/vendors/")
        vendors = response.json()
        vendor_id = next(v["id"] for v in vendors if v["name"] == "TestVendorHP")
        print(f"Found existing vendor ID: {vendor_id}")
    else:
        print("Failed to create vendor:", response.status_code, response.text)
        return

    # 2. Create PrinterType
    pt_data = {
        "vendor_id": vendor_id,
        "name": "TestModelX",
        "protocol": "SNMP",
        "discovery_config": {"oid": "1.3.6.1.2.1.1.1.0"}
    }
    response = requests.post(f"{API_URL}/printer-types/", json=pt_data)
    if response.status_code == 200:
        print("PrinterType created successfully:", response.json())
    else:
        print("Failed to create printer type:", response.status_code, response.text)

    # 3. List Vendors
    response = requests.get(f"{API_URL}/vendors/")
    print("Vendors List:", response.json())

    # 4. List PrinterTypes
    response = requests.get(f"{API_URL}/printer-types/")
    print("PrinterTypes List:", response.json())

if __name__ == "__main__":
    test_master_data()
