from sqlalchemy.orm import Session
import models, schemas

def get_printer(db: Session, printer_id: int):
    from sqlalchemy.orm import joinedload
    return db.query(models.Printer)\
             .options(joinedload(models.Printer.last_web_crawl))\
             .filter(models.Printer.id == printer_id).first()

def get_printer_by_ip(db: Session, ip_address: str):
    return db.query(models.Printer).filter(models.Printer.ip_address == ip_address).first()

def get_printers(db: Session, skip: int = 0, limit: int = 100):
    from sqlalchemy.orm import joinedload
    return db.query(models.Printer)\
             .options(joinedload(models.Printer.last_web_crawl))\
             .offset(skip).limit(limit).all()

def create_printer(db: Session, printer: schemas.PrinterCreate):
    db_printer = models.Printer(
        name=printer.name,
        ip_address=printer.ip_address,
        model=printer.model,
        location=printer.location,
        printer_type_id=printer.printer_type_id
    )
    db.add(db_printer)
    db.commit()
    db.refresh(db_printer)
    
    # Log creation
    create_printer_log(db, schemas.PrinterLogCreate(
        printer_id=db_printer.id,
        event_type="creation",
        new_value=db_printer.name,
        message=f"Printer created with IP {db_printer.ip_address}"
    ))
    
    return db_printer

def update_printer(db: Session, printer_id: int, printer: schemas.PrinterUpdate):
    db_printer = get_printer(db, printer_id)
    if db_printer:
        update_data = printer.dict(exclude_unset=True)
        
        # Track important changes for logging
        for key, value in update_data.items():
            old_val = getattr(db_printer, key)
            if old_val != value and key in ["status", "ip_address", "name", "model"]:
                create_printer_log(db, schemas.PrinterLogCreate(
                    printer_id=printer_id,
                    event_type=f"{key}_change",
                    old_value=str(old_val) if old_val is not None else None,
                    new_value=str(value) if value is not None else None,
                    message=f"{key.capitalize()} changed from {old_val} to {value}"
                ))
            setattr(db_printer, key, value)
        
        db.commit()
        return get_printer(db, printer_id)

def delete_printer(db: Session, printer_id: int):
    db_printer = db.query(models.Printer).filter(models.Printer.id == printer_id).first()
    if db_printer:
        db.delete(db_printer)
        db.commit()
    return db_printer

# --- Vendor CRUD ---
def get_vendor(db: Session, vendor_id: int):
    return db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()

def get_vendor_by_name(db: Session, name: str):
    return db.query(models.Vendor).filter(models.Vendor.name == name).first()

def get_vendors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Vendor).offset(skip).limit(limit).all()

def create_vendor(db: Session, vendor: schemas.VendorCreate):
    db_vendor = models.Vendor(name=vendor.name)
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

def update_vendor(db: Session, vendor_id: int, name: str):
    db_vendor = get_vendor(db, vendor_id)
    if db_vendor:
        db_vendor.name = name
        db.commit()
        db.refresh(db_vendor)
    return db_vendor

def delete_vendor(db: Session, vendor_id: int):
    db_vendor = get_vendor(db, vendor_id)
    if db_vendor:
        db.delete(db_vendor)
        db.commit()
    return db_vendor

# --- PrinterType CRUD ---
def get_printer_type(db: Session, printer_type_id: int):
    from sqlalchemy.orm import joinedload
    return db.query(models.PrinterType)\
             .options(joinedload(models.PrinterType.vendor))\
             .filter(models.PrinterType.id == printer_type_id).first()

def get_printer_types(db: Session, skip: int = 0, limit: int = 100):
    from sqlalchemy.orm import joinedload
    return db.query(models.PrinterType)\
             .options(joinedload(models.PrinterType.vendor))\
             .offset(skip).limit(limit).all()

def create_printer_type(db: Session, printer_type: schemas.PrinterTypeCreate):
    db_printer_type = models.PrinterType(
        vendor_id=printer_type.vendor_id,
        name=printer_type.name,
        probes=printer_type.probes,
        discovery_config=printer_type.discovery_config
    )
    db.add(db_printer_type)
    db.commit()
    db.refresh(db_printer_type)
    return db_printer_type

def update_printer_type(db: Session, printer_type_id: int, printer_type: schemas.PrinterTypeCreate):
    db_type = get_printer_type(db, printer_type_id)
    if db_type:
        db_type.vendor_id = printer_type.vendor_id
        db_type.name = printer_type.name
        db_type.probes = printer_type.probes
        db_type.discovery_config = printer_type.discovery_config
        db.commit()
        db.refresh(db_type)
    return db_type

def delete_printer_type(db: Session, printer_type_id: int):
    db_type = get_printer_type(db, printer_type_id)
    if db_type:
        db.delete(db_type)
        db.commit()
    return db_type

# --- PrinterLog CRUD ---
def get_printer_logs(db: Session, printer_id: int, limit: int = 50):
    return db.query(models.PrinterLog)\
             .filter(models.PrinterLog.printer_id == printer_id)\
             .order_by(models.PrinterLog.timestamp.desc())\
             .limit(limit).all()

def create_printer_log(db: Session, log: schemas.PrinterLogCreate):
    db_log = models.PrinterLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def save_web_crawl(db: Session, printer_id: int, content: str):
    db_crawl = db.query(models.PrinterWebCrawl).filter(models.PrinterWebCrawl.printer_id == printer_id).first()
    if db_crawl:
        db_crawl.content = content
        db_crawl.timestamp = func.now()
    else:
        db_crawl = models.PrinterWebCrawl(printer_id=printer_id, content=content)
        db.add(db_crawl)
    db.commit()
    db.refresh(db_crawl)
    return db_crawl
