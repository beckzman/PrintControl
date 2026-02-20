from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Vendor Schemas ---
class VendorBase(BaseModel):
    name: str

class VendorCreate(VendorBase):
    pass

class Vendor(VendorBase):
    id: int
    
    class Config:
        from_attributes = True

# --- PrinterType Schemas ---
class PrinterTypeBase(BaseModel):
    name: str
    probes: List[str] = ["ping"]
    discovery_config: Dict[str, Any] = {}

class PrinterTypeCreate(PrinterTypeBase):
    vendor_id: int

class PrinterType(PrinterTypeBase):
    id: int
    vendor_id: int
    vendor: Optional[Vendor] = None

    class Config:
        from_attributes = True

# --- Printer Schemas ---
# --- Printer Schemas ---
class PrinterBase(BaseModel):
    name: str
    ip_address: str
    model: Optional[str] = None
    location: Optional[str] = None
    printer_type_id: Optional[int] = None

class PrinterCreate(PrinterBase):
    pass

class PrinterUpdate(BaseModel):
    status: Optional[str] = None
    name: Optional[str] = None
    ip_address: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    last_protocol: Optional[str] = None
    sys_location: Optional[str] = None
    sys_description: Optional[str] = None
    printer_type_id: Optional[int] = None

class Printer(PrinterBase):
    id: int
    status: str
    last_updated: Optional[datetime] = None
    last_protocol: Optional[str] = None
    sys_location: Optional[str] = None
    sys_description: Optional[str] = None
    printer_type: Optional['PrinterType'] = None
    last_web_crawl: Optional['WebCrawl'] = None

    class Config:
        from_attributes = True

# --- PrinterLog Schemas ---
class PrinterLogBase(BaseModel):
    event_type: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    message: Optional[str] = None

class PrinterLogCreate(PrinterLogBase):
    printer_id: int

class PrinterLog(PrinterLogBase):
    id: int
    printer_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# --- Web Crawl Schemas ---
class WebCrawlBase(BaseModel):
    content: str

class WebCrawlCreate(WebCrawlBase):
    printer_id: int

class WebCrawl(WebCrawlBase):
    id: int
    printer_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class ScanResponse(BaseModel):
    printer: Printer
    reached: bool
