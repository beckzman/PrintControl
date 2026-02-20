import asyncio
import time
from database import SessionLocal
import crud
from protocols.scanner import update_printer_status

async def start_status_updates():
    """
    Background task that updates all printers every 15 minutes.
    """
    # Wait a bit after startup to let the app initialize
    await asyncio.sleep(10)
    
    while True:
        try:
            print("Background Job: Starting status update for all printers...")
            db = SessionLocal()
            try:
                printers = crud.get_printers(db, limit=1000)
                for printer in printers:
                    try:
                        print(f"Background Job: Updating {printer.name} ({printer.ip_address})...")
                        update_printer_status(db, printer.id)
                    except Exception as e:
                        print(f"Background Job: Error updating printer {printer.id}: {e}")
            finally:
                db.close()
            
            print("Background Job: All printers updated. Sleeping for 15 minutes...")
        except Exception as e:
            print(f"Background Job: Global error in scheduler: {e}")
            
        # Sleep for 15 minutes (900 seconds)
        await asyncio.sleep(900)
