"""Set a folder up as an SEO project: seo-project.json plus an empty keyword map.

  python init_project.py --domain example.com --country Canada --city "Denver,Colorado,United States"
                         [--language en] [--competitors a.com,b.com] [--service-lines "Plumbing,Drains"]
                         [--map keyword-map.xlsx] [--data-dir seo-data]

Never overwrites: an existing config or workbook is left alone and checked instead.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c  # noqa: E402


def make_workbook(path: Path):
    import openpyxl
    from openpyxl.styles import Font
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Keyword map"
    ws.append(c.MAP_COLUMNS)
    rt = wb.create_sheet("Rank tracker")
    rt.append(["Keyword"])
    tr = wb.create_sheet("Draft list triage")
    tr.append(c.TRIAGE_COLUMNS)
    for s in wb.worksheets:
        for cell in s[1]:
            cell.font = Font(bold=True)
        s.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{ws.cell(1, len(c.MAP_COLUMNS)).column_letter}1"
    wb.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", required=True)
    ap.add_argument("--country", required=True, help="DataForSEO location name, e.g. Canada, United States")
    ap.add_argument("--city", required=True, help='SERP location, e.g. "Denver,Colorado,United States"')
    ap.add_argument("--language", default="en")
    ap.add_argument("--competitors", default="")
    ap.add_argument("--service-lines", default="")
    ap.add_argument("--map", default="keyword-map.xlsx")
    ap.add_argument("--data-dir", default="seo-data")
    a = ap.parse_args()
    root = Path.cwd()
    cfgp = root / c.CONFIG_NAME
    if cfgp.exists():
        print(f"{c.CONFIG_NAME} already exists; left as it is.")
    else:
        t = json.loads((c.SKILL_DIR / "assets" / "seo-project.template.json").read_text(encoding="utf-8"))
        t["domain"] = a.domain.lower().removeprefix("https://").removeprefix("http://").removeprefix("www.").strip("/")
        t["market"].update({"country": a.country, "language_code": a.language, "default_serp_location": a.city})
        city = a.city.split(",")[0].strip().lower()
        t["places"] = {city: a.city}
        t["research"]["places"] = [city]
        t["competitors"] = [x.strip() for x in a.competitors.split(",") if x.strip()]
        t["service_lines"] = [x.strip() for x in a.service_lines.split(",") if x.strip()] or ["Main"]
        t["map"]["path"] = a.map
        t["data_dir"] = a.data_dir
        cfgp.write_text(json.dumps(t, indent=2), encoding="utf-8")
        print(f"Wrote {cfgp}. Fill in research.services, places, competitor_brands and priority_rules next "
              "(reference/config.md).")
    cfg, _ = c.load_config()
    mp = c.map_path(cfg, root)
    if mp.exists():
        wb, ws = c.open_map(cfg, root, read_only=True)
        c.header_index(ws, cfg)  # stops with the missing column names if the sheet doesn't fit
        print(f"{mp.name} already exists and has the columns the scripts need.")
    else:
        try:
            make_workbook(mp)
        except ImportError:
            c.die("openpyxl is missing. Install it with: pip install openpyxl")
        print(f"Created {mp.name} with the Keyword map, Rank tracker and Draft list triage sheets.")
    c.data_dir(cfg, root)
    print("Next: python status.py")


if __name__ == "__main__":
    main()
