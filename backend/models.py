from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    printer_types = relationship("PrinterType", back_populates="vendor")

class PrinterType(Base):
    __tablename__ = "printer_types"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    name = Column(String)
    protocol = Column(String) # 'SNMP' or 'WEB'
    discovery_config = Column(JSON) # e.g. {"oid": "1.3.6.1..."} or {"selector": "#id"}

    vendor = relationship("Vendor", back_populates="printer_types")

class Printer(Base):
    __tablename__ = "printers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    ip_address = Column(String, unique=True, index=True)
    model = Column(String)
    location = Column(String)
    status = Column(String, default="Unknown")
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    printer_type_id = Column(Integer, ForeignKey("printer_types.id"), nullable=True)

    printer_type = relationship("PrinterType")
