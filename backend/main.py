from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud, models, schemas
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Printer Management API")

# CORS configuration
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/printers", response_model=schemas.Printer)
def create_printer(printer: schemas.PrinterCreate, db: Session = Depends(get_db)):
    db_printer = crud.get_printer_by_ip(db, ip_address=printer.ip_address)
    if db_printer:
        raise HTTPException(status_code=400, detail="Printer with this IP already exists")
    return crud.create_printer(db=db, printer=printer)

@app.get("/printers", response_model=List[schemas.Printer])
def read_printers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    printers = crud.get_printers(db, skip=skip, limit=limit)
    return printers

@app.get("/printers/{printer_id}", response_model=schemas.Printer)
def read_printer(printer_id: int, db: Session = Depends(get_db)):
    db_printer = crud.get_printer(db, printer_id=printer_id)
    if db_printer is None:
        raise HTTPException(status_code=404, detail="Printer not found")
    return db_printer

@app.put("/printers/{printer_id}", response_model=schemas.Printer)
def update_printer(printer_id: int, printer: schemas.PrinterUpdate, db: Session = Depends(get_db)):
    db_printer = crud.update_printer(db, printer_id=printer_id, printer=printer)
    if db_printer is None:
        raise HTTPException(status_code=404, detail="Printer not found")
    return db_printer

@app.get("/printers/{printer_id}/logs", response_model=List[schemas.PrinterLog])
def read_printer_logs(printer_id: int, db: Session = Depends(get_db)):
    return crud.get_printer_logs(db, printer_id=printer_id)

from protocols import snmp, web, ping, dns, scanner
import scheduler
import asyncio

@app.post("/printers/{printer_id}/scan", response_model=schemas.ScanResponse)
def scan_printer(printer_id: int, protocol: str = None, db: Session = Depends(get_db)):
    updated_printer, reached = scanner.update_printer_status(db, printer_id, forced_protocol=protocol)
    if not updated_printer:
        raise HTTPException(status_code=404, detail="Printer not found")
    return {"printer": updated_printer, "reached": reached}

@app.delete("/printers/{printer_id}")
def delete_printer(printer_id: int, db: Session = Depends(get_db)):
    db_printer = crud.delete_printer(db, printer_id)
    if not db_printer:
        raise HTTPException(status_code=404, detail="Printer not found")
    return {"message": "Printer deleted successfully"}

# --- Vendor Endpoints ---
@app.post("/vendors", response_model=schemas.Vendor)
def create_vendor(vendor: schemas.VendorCreate, db: Session = Depends(get_db)):
    db_vendor = crud.get_vendor_by_name(db, name=vendor.name)
    if db_vendor:
        raise HTTPException(status_code=400, detail="Vendor already exists")
    return crud.create_vendor(db=db, vendor=vendor)

@app.get("/vendors", response_model=List[schemas.Vendor])
def read_vendors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    vendors = crud.get_vendors(db, skip=skip, limit=limit)
    return vendors

@app.put("/vendors/{vendor_id}", response_model=schemas.Vendor)
def update_vendor(vendor_id: int, vendor: schemas.VendorCreate, db: Session = Depends(get_db)):
    db_vendor = crud.update_vendor(db, vendor_id, vendor.name)
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return db_vendor

@app.delete("/vendors/{vendor_id}")
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    crud.delete_vendor(db, vendor_id)
    return {"message": "Vendor deleted"}

# --- PrinterType Endpoints ---
@app.post("/printer-types", response_model=schemas.PrinterType)
def create_printer_type(printer_type: schemas.PrinterTypeCreate, db: Session = Depends(get_db)):
    # Verify vendor exists
    db_vendor = crud.get_vendor(db, vendor_id=printer_type.vendor_id)
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return crud.create_printer_type(db=db, printer_type=printer_type)

@app.get("/printer-types", response_model=List[schemas.PrinterType])
def read_printer_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    printer_types = crud.get_printer_types(db, skip=skip, limit=limit)
    return printer_types

@app.put("/printer-types/{printer_type_id}", response_model=schemas.PrinterType)
def update_printer_type(printer_type_id: int, printer_type: schemas.PrinterTypeCreate, db: Session = Depends(get_db)):
    db_type = crud.update_printer_type(db, printer_type_id, printer_type)
    if not db_type:
        raise HTTPException(status_code=404, detail="Printer Type not found")
    return db_type

@app.delete("/printer-types/{printer_type_id}")
def delete_printer_type(printer_type_id: int, db: Session = Depends(get_db)):
    crud.delete_printer_type(db, printer_type_id)
    return {"message": "Printer Type deleted"}

@app.on_event("startup")
async def startup_event():
    # Start background status updates
    asyncio.create_task(scheduler.start_status_updates())

# --- Detection Endpoint ---
from protocols import ping, snmp, web, dns

@app.post("/printers/resolve")
def resolve_printer(data: dict):
    hostname = data.get("hostname")
    if not hostname:
        raise HTTPException(status_code=400, detail="Hostname required")
    
    ip = dns.resolve_hostname(hostname)
    if not ip:
        raise HTTPException(status_code=404, detail="Hostname could not be resolved")
    
    return {"ip_address": ip}

@app.post("/printers/detect")
def detect_printer(data: dict):
    ip_address = data.get("ip_address")
    if not ip_address:
        raise HTTPException(status_code=400, detail="IP Address required")

    result = {
        "online": False,
        "model": None,
        "vendor_id": None,
        "status": "Offline",
        "probes": []
    }

    # 1. Ping
    if ping.ping_host(ip_address):
        result["online"] = True
        result["status"] = "Online" # Default if nothing else found
    else:
        return result # Early return if offline

    # 2. SNMP (Try public community)
    try:
        snmp_data = snmp.scan_printer(ip_address)
        if snmp_data and snmp_data.get("model") and "Generic" not in snmp_data.get("model"):
             result["model"] = snmp_data["model"]
             result["status"] = snmp_data.get("status", "Ready")
             result["probes"] = ["ping", "snmp"]
    except Exception as e:
        print(f"SNMP Detect failed: {e}")

    # 3. Web (Fallback or refinement)
    if not result["model"]:
        try:
            web_data = web.scan_printer(ip_address)
            if web_data and web_data.get("model") and "Unknown" not in web_data.get("model"):
                result["model"] = web_data["model"]
                result["status"] = web_data.get("status", result["status"])
                result["probes"] = ["ping", "web"]
        except Exception as e:
            print(f"Web Detect failed: {e}")

    # 4. Attempt Vendor Matching (Basic)
    if result["model"]:
        model_lower = result["model"].lower()
        db = SessionLocal()
        try:
            vendors = crud.get_vendors(db)
            for v in vendors:
                if v.name.lower() in model_lower:
                    result["vendor_id"] = v.id
                    break
        finally:
            db.close()

    return result
