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
    protocol: str
    discovery_config: Dict[str, Any]

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
    printer_type_id: Optional[int] = None

class Printer(PrinterBase):
    id: int
    status: str
    last_updated: Optional[datetime] = None
    printer_type: Optional['PrinterType'] = None

    class Config:
        from_attributes = True
