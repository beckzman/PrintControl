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
    probes = Column(JSON, default=list) # e.g. ["ping", "snmp", "web"]
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
    last_protocol = Column(String, nullable=True)
    sys_location = Column(String, nullable=True)
    sys_description = Column(String, nullable=True)
    printer_type_id = Column(Integer, ForeignKey("printer_types.id"), nullable=True)

    printer_type = relationship("PrinterType")
    logs = relationship("PrinterLog", back_populates="printer", cascade="all, delete-orphan")
    last_web_crawl = relationship("PrinterWebCrawl", back_populates="printer", uselist=False, cascade="all, delete-orphan")

class PrinterLog(Base):
    __tablename__ = "printer_logs"

    id = Column(Integer, primary_key=True, index=True)
    printer_id = Column(Integer, ForeignKey("printers.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    event_type = Column(String) # 'status_change', 'config_change', 'creation'
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    message = Column(String, nullable=True)

    printer = relationship("Printer", back_populates="logs")

class PrinterWebCrawl(Base):
    __tablename__ = "printer_web_crawls"

    id = Column(Integer, primary_key=True, index=True)
    printer_id = Column(Integer, ForeignKey("printers.id"), unique=True)
    content = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    printer = relationship("Printer", back_populates="last_web_crawl")
