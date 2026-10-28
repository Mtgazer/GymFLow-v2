#!/usr/bin/env python3
"""Automated tool to capture genuine screenshots of GymFlow-v2 GUI windows."""
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import Xlib.display
import Xlib.X
from PIL import Image

from app import GymFlow
from core.container import Container

OUTPUT_DIR = PROJECT_ROOT / "docs" / "screenshots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def capture_window_pixmap(window_id: int, output_path: Path):
    """Directly extracts window pixels from Xwayland buffer via python-xlib."""
    display = Xlib.display.Display()
    xwin = display.create_resource_object("window", window_id)
    geom = xwin.get_geometry()
    raw = xwin.get_image(0, 0, geom.width, geom.height, Xlib.X.ZPixmap, 0xFFFFFFFF)
    img = Image.frombytes("RGB", (geom.width, geom.height), raw.data, "raw", "BGRX")
    img.save(str(output_path))
    print(f"[SUCCESS] Saved screenshot: {output_path.name} ({geom.width}x{geom.height}, {output_path.stat().st_size} bytes)")


def seed_sample_data(container: Container):
    """Seeds realistic members for realistic visual presentation."""
    service = container.member_service
    sample_members = [
        ("Ahmed Ali", "01012345678", "Premium", 350.0),
        ("Sara Hassan", "01198765432", "Gold", 500.0),
        ("Omar Nader", "01234567890", "Basic", 250.0),
        ("Nourhan Tarek", "01555667788", "VIP Annual", 3500.0),
    ]
    for name, phone, plan, price in sample_members:
        existing = service.get_member_by_phone(phone)
        if not existing:
            service.register_member(name, phone, plan, price)
    print("[INFO] Sample members seeded for screenshot demonstration.")


def main():
    print("Launching GymFlow for screenshot capture...")
    app = GymFlow()
    app.geometry("1200x700+50+50")
    app.update()

    seed_sample_data(app.container)
    app.dashboard_page.refresh_dashboard()
    app.members_page.refresh_members()

    def do_captures():
        try:
            # 1. Capture Dashboard View
            app.show_page("dashboard")
            app.update_idletasks()
            time.sleep(0.5)
            capture_window_pixmap(app.winfo_id(), OUTPUT_DIR / "dashboard_view.png")

            # 2. Capture Members View
            app.show_page("members")
            app.update_idletasks()
            time.sleep(0.5)
            capture_window_pixmap(app.winfo_id(), OUTPUT_DIR / "members_view.png")

            # 3. Capture Add Member Dialog
            app.members_page.open_add_dialog()
            app.update_idletasks()
            time.sleep(0.5)

            # Find toplevel dialog window
            toplevels = [w for w in app.winfo_children() if isinstance(w, type(app.members_page)) or "toplevel" in str(type(w)).lower()]
            dialog = None
            for child in app.winfo_children():
                if hasattr(child, "geometry") and child != app.content and child != app.sidebar:
                    dialog = child
                    break

            if dialog:
                capture_window_pixmap(dialog.winfo_id(), OUTPUT_DIR / "add_member_dialog.png")
                dialog.destroy()
            else:
                # Capture main window with modal active
                capture_window_pixmap(app.winfo_id(), OUTPUT_DIR / "add_member_dialog.png")

        except Exception as e:
            print(f"[ERROR] Capture failed: {e}")
        finally:
            app.destroy()

    app.after(1000, do_captures)
    app.mainloop()


if __name__ == "__main__":
    main()
