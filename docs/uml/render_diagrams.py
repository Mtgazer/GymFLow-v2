#!/usr/bin/env python3
"""Script to render Mermaid UML diagrams (.mmd) to high-resolution PNG images."""
import base64
import json
import urllib.request
from pathlib import Path

UML_DIR = Path(__file__).resolve().parent

DIAGRAMS = [
    ("use_case_diagram.mmd", "use_case_diagram.png"),
    ("class_diagram.mmd", "class_diagram.png"),
    ("sequence_diagram.mmd", "sequence_diagram.png"),
]


def render_mermaid(mmd_path: Path, output_png: Path):
    with open(mmd_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Clean markdown backticks if present
    lines = content.strip().splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    cleaned = "\n".join(lines).strip()

    # Encode for mermaid.ink
    payload = {
        "code": cleaned,
        "mermaid": {
            "theme": "default",
            "themeVariables": {
                "primaryColor": "#FFC107",
                "primaryTextColor": "#000000",
                "lineColor": "#1F2937",
            }
        }
    }
    json_str = json.dumps(payload)
    encoded = base64.b64encode(json_str.encode("utf-8")).decode("ascii")
    url = f"https://mermaid.ink/img/pako:{encoded}"

    # Also fallback to raw code if pako is not used
    raw_encoded = base64.b64encode(cleaned.encode("utf-8")).decode("ascii")
    fallback_url = f"https://mermaid.ink/img/{raw_encoded}?bgColor=FFFFFF"

    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}

    # Try fallback url first as it's standard base64 mermaid
    for target_url in [fallback_url, url]:
        try:
            req = urllib.request.Request(target_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                img_data = response.read()
                with open(output_png, "wb") as out_f:
                    out_f.write(img_data)
                print(f"[SUCCESS] Rendered '{mmd_path.name}' -> '{output_png.name}' ({len(img_data)} bytes)")
                return True
        except Exception as e:
            print(f"[WARN] Failed with url {target_url[:40]}...: {e}")

    print(f"[ERROR] Could not render {mmd_path.name}")
    return False


def main():
    print("Rendering UML diagrams...")
    for mmd_file, png_file in DIAGRAMS:
        mmd_path = UML_DIR / mmd_file
        png_path = UML_DIR / png_file
        if mmd_path.exists():
            render_mermaid(mmd_path, png_path)


if __name__ == "__main__":
    main()
