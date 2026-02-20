from database import SessionLocal, engine, Base
import models


def seed():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Vendors
        hp = db.query(models.Vendor).filter_by(name="HP").first()
        if not hp:
            hp = models.Vendor(name="HP")
            db.add(hp)
            db.commit()
            db.refresh(hp)

        epson = db.query(models.Vendor).filter_by(name="Epson").first()
        if not epson:
            epson = models.Vendor(name="Epson")
            db.add(epson)
            db.commit()
            db.refresh(epson)

        # Printer types
        pt1 = db.query(models.PrinterType).filter_by(name="LaserJet Pro").first()
        if not pt1:
            pt1 = models.PrinterType(
                vendor_id=hp.id,
                name="LaserJet Pro",
                probes=["ping", "snmp"],
                discovery_config={"oid": "1.3.6.1.2.1.1.1.0"}
            )
            db.add(pt1)
            db.commit()
            db.refresh(pt1)

        pt2 = db.query(models.PrinterType).filter_by(name="Epson WorkForce").first()
        if not pt2:
            pt2 = models.PrinterType(
                vendor_id=epson.id,
                name="Epson WorkForce",
                probes=["ping", "web"],
                discovery_config={"selector": "#model"}
            )
            db.add(pt2)
            db.commit()
            db.refresh(pt2)

        # Printers
        p1 = db.query(models.Printer).filter_by(ip_address="192.168.1.10").first()
        if not p1:
            p1 = models.Printer(
                name="Office HP",
                ip_address="192.168.1.10",
                model="LaserJet Pro M404",
                location="Office 1",
                status="Online",
                last_protocol="ping",
                sys_location="Office 1",
                sys_description="HP LaserJet",
                printer_type_id=pt1.id
            )
            db.add(p1)
            db.commit()
            db.refresh(p1)

            # Log and web crawl
            log = models.PrinterLog(printer_id=p1.id, event_type="creation", new_value=p1.name, message="Seeded printer")
            db.add(log)
            db.commit()

            crawl = models.PrinterWebCrawl(printer_id=p1.id, content="<html>HP status OK</html>")
            db.add(crawl)
            db.commit()

        p2 = db.query(models.Printer).filter_by(ip_address="192.168.1.11").first()
        if not p2:
            p2 = models.Printer(
                name="Lobby Epson",
                ip_address="192.168.1.11",
                model="WorkForce WF-2860",
                location="Lobby",
                status="Ready",
                last_protocol="snmp",
                sys_location="Lobby",
                sys_description="Epson WorkForce",
                printer_type_id=pt2.id
            )
            db.add(p2)
            db.commit()
            db.refresh(p2)

            log = models.PrinterLog(printer_id=p2.id, event_type="creation", new_value=p2.name, message="Seeded printer")
            db.add(log)
            db.commit()

            crawl = models.PrinterWebCrawl(printer_id=p2.id, content="<html>Epson details</html>")
            db.add(crawl)
            db.commit()

        print("Seeding complete")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
