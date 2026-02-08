# PrintControl

A modern, glassmorphism-inspired printer management system. Automatically detect, monitor, and manage your network printers using SNMP, Web scraping, and ICMP.

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- `snmpget` utility installed on the system (for SNMP detection)

### Backend Setup
1. `cd backend`
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `uvicorn main:app --reload --port 8000`

### Frontend Setup
1. `cd frontend`
2. Install dependencies: `npm install`
3. Run: `npm start`
4. Access at: [http://localhost:4200](http://localhost:4200)

## 📊 Infrastructure & Monitoring

### Printer Status Detection
The system uses a tiered approach to determine if a printer is healthy:
1. **Ping (ICMP):** Checks if the device is reachable on the network.
2. **SNMP:** Queries `sysDescr` for model information and general readiness.
3. **Web (HTTP):** Scrapes the printer's internal web interface for high-fidelity data (Model, Vendor, Detailed Status).

### 🟢 Status Indicators (Green Light)
Printers display a status indicator in the UI. A **"Green Light"** (Glow) is triggered under the following conditions:

| Status | Color | Meaning |
| :--- | :--- | :--- |
| **Online** | 🟢 Green | Responding to Ping. |
| **Ready** | 🟢 Green | Confirmed operational via SNMP or Web. |
| **Printing** | 🟢 Green | Currently processing a job, but healthy. |
| **Offline** | 🔴 Red | No network response (Ping failed). |
| **Error** | 🔴 Red | Hardware fault reported by the device. |
| **Unknown** | ⚪ Gray | Initial state or inconclusive scan results. |

## 🛠 Features
- **Auto-Detection:** Enter an IP or Hostname to automatically detect vendor and model.
- **DNS Resolution:** Resolve hostnames to IPs directly within the "Add Printer" modal.
- **Multiple Protocols:** Support for SNMP and Web-based status monitoring.
- **Modern UI:** Glassmorphism design with responsive grid and list views.
