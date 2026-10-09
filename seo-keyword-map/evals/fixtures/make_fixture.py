"""Build the synthetic test project evals/fixtures/acme/ (an invented Calgary plumber).

  python evals/fixtures/make_fixture.py

Everything here is made up. Real client data never goes in this public repo.
The fixture is shaped to exercise the method:
  - explainer keywords sitting on service pages (should move to posts)
  - two planned cost posts whose SERPs are the same (should merge)
  - an association-led keyword (never a Primary)
  - research candidates covering every triage outcome
"""
import csv
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "acme"
sys.path.insert(0, str(HERE.parent.parent / "scripts"))
import common as c  # noqa: E402
from init_project import make_workbook  # noqa: E402

# keyword, volume, kd, line, intent, page, exists, role, type
ROWS = [
    ("plumbers calgary", 880, 22, "Plumbing", "Local", "/plumbing/", "Yes", "Primary", "hub"),
    ("plumbing services calgary", 210, 18, "Plumbing", "Local", "/plumbing/", "Yes", "Secondary", "hub"),
    ("calgary plumbing companies", 70, 15, "Plumbing", "Local", "/plumbing/", "Yes", "Support", "hub"),
    ("alberta plumbing association", 90, 5, "Plumbing", "Commercial", "/plumbing/", "Yes", "Support", "hub"),
    ("drain cleaning", 480, 20, "Drains", "Commercial", "/drain-cleaning/", "Yes", "Primary", "service"),
    ("drain cleaning cost", 320, 9, "Drains", "Commercial", "/drain-cleaning/", "Yes", "Secondary", "service"),
    ("how to unclog a drain", 260, 14, "Drains", "Informational", "/drain-cleaning/", "Yes", "Support", "service"),
    ("water heater installation", 390, 25, "Plumbing", "Commercial", "/water-heater-installation/", "Yes", "Primary", "service"),
    ("how long does a water heater last", 170, 11, "Plumbing", "Informational", "/water-heater-installation/", "Yes", "Support", "service"),
    ("tankless vs tank water heater", 140, 16, "Plumbing", "Informational", "/water-heater-installation/", "Yes", "Support", "service"),
    ("plumber cost", 210, 8, "Plumbing", "Commercial", "/blog/plumber-cost/", "No", "Primary", "post"),
    ("how much does a plumber charge", 170, 7, "Plumbing", "Informational", "/blog/plumber-cost/", "No", "Secondary", "post"),
    ("drain cleaning price", 90, 6, "Drains", "Commercial", "/blog/drain-cleaning-price/", "No", "Primary", "post"),
    ("emergency plumber calgary", 260, 19, "Plumbing", "Local", "/emergency-plumbing/", "No", "Primary", "service"),
]


def urls(prefix, n, start=0):
    return [f"{prefix}{i}" for i in range(start, start + n)]


# Synthetic SERPs. Shared URL blocks create the overlaps the scenarios depend on.
COST_POOL = urls("costguide.example/plumbing-cost-", 8)
LOCAL_FIRMS = [f"firm{i}.example/" for i in range(6)]
SNAP = {
    "plumbers calgary": ("SERVICE+local", {"svc": 0.3, "home": 0.4, "dir": 0.3}, LOCAL_FIRMS + urls("yelp.ca/biz/p", 4)),
    "plumbing services calgary": ("SERVICE+local", {"svc": 0.5, "home": 0.4, "dir": 0.1}, LOCAL_FIRMS + urls("firm0.example/services/", 4)),
    "calgary plumbing companies": ("SERVICE+local", {"svc": 0.3, "home": 0.5, "dir": 0.2}, LOCAL_FIRMS + urls("homestars.com/c", 3)),
    "alberta plumbing association": ("DIRECTORY/ORG", {"org": 0.7, "svc": 0.2, "soc": 0.1}, urls("alberta.ca/trades/", 5) + urls("linkedin.com/company/apa", 3)),
    "drain cleaning": ("SERVICE+local", {"svc": 0.8, "home": 0.1, "dir": 0.1}, urls("firm1.example/drain-cleaning", 6) + urls("firm2.example/drains/", 4)),
    "drain cleaning cost": ("ARTICLE", {"art": 0.8, "svc": 0.1, "soc": 0.1}, COST_POOL[:7] + urls("reddit.com/r/plumbing/c", 3)),
    "how to unclog a drain": ("ARTICLE", {"art": 0.7, "soc": 0.3}, urls("diy.example/how-to-unclog-", 7) + urls("youtube.com/watch?v=u", 3)),
    "water heater installation": ("SERVICE+local", {"svc": 0.8, "home": 0.2}, urls("firm3.example/water-heaters/", 8) + LOCAL_FIRMS[:2]),
    "how long does a water heater last": ("ARTICLE", {"art": 0.9, "soc": 0.1}, urls("energy.example/what-is-water-heater-life-", 9) + ["reddit.com/r/hvac/x"]),
    "tankless vs tank water heater": ("ARTICLE", {"art": 1.0}, urls("compare.example/tankless-vs-tank-", 10)),
    "plumber cost": ("ARTICLE", {"art": 0.9, "dir": 0.1}, COST_POOL + urls("homeadvisor.com/cost/p", 2)),
    "how much does a plumber charge": ("ARTICLE", {"art": 0.9, "soc": 0.1}, COST_POOL[1:] + ["reddit.com/r/plumbing/q", "costguide.example/x"]),
    "drain cleaning price": ("ARTICLE", {"art": 0.9, "soc": 0.1}, COST_POOL[:6] + urls("reddit.com/r/plumbing/p", 4)),
    "emergency plumber calgary": ("SERVICE+local", {"svc": 0.5, "home": 0.5}, LOCAL_FIRMS + urls("firm4.example/emergency/", 4)),
}

CANDIDATES = [
    ("plumber jobs calgary", 390, "grid"), ("rival plumbing reviews", 210, "competitor"),
    ("drain cleaning toronto", 320, "competitor"), ("drains cleaning calgary", 30, "suggest"),
    ("sump pump installation calgary", 90, "grid"), ("calgary zoning map", 880, "serp"),
    ("water heater repair calgary", 170, "grid"), ("what size water heater do i need", 140, "serp"),
    ("plumbing", 40500, "serp"), ("toilet repair airdrie", 10, "grid"),
]


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "seo-data" / "serp").mkdir(parents=True)
    (OUT / "seo-data" / "research").mkdir(parents=True)
    cfg = json.loads((HERE.parent.parent / "assets" / "seo-project.template.json").read_text(encoding="utf-8"))
    cfg.update({"domain": "acme-plumbing.ca", "service_lines": ["Plumbing", "Drains"],
                "competitors": ["rivalplumbing.example"], "competitor_brands": ["rival"],
                "out_of_area_patterns": ["toronto", "vancouver", "ontario"],
                "notes": "Emergency plumbing gets its own page (client decision). Posts live at /slug/, no /blog/."})
    cfg["market"].update({"default_serp_location": "Calgary,Alberta,Canada"})
    cfg["places"] = {"calgary": "Calgary,Alberta,Canada", "airdrie": None}
    cfg["research"] = {"services": ["plumber", "drain cleaning", "water heater installation"], "places": ["calgary", "airdrie"]}
    cfg["priority_rules"] = [{"service_line": "*", "page_types": ["hub", "service", "location"], "priority": 1},
                             {"service_line": "*", "page_types": ["post"], "priority": 2}]
    cfg["copy_from"] = {"post": "/blog-sample/"}
    cfg["url_conventions"] = "Posts at /slug/ with no /blog/ prefix."
    (OUT / "seo-project.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")

    import openpyxl
    make_workbook(OUT / "keyword-map.xlsx")
    wb = openpyxl.load_workbook(OUT / "keyword-map.xlsx")
    ws = wb["Keyword map"]
    vol = {}
    for k, v, kd, line, intent, page, ex, role, ptype in ROWS:
        vol[page] = vol.get(page, 0) + v
    for k, v, kd, line, intent, page, ex, role, ptype in ROWS:
        ws.append([line, k, v, kd, intent, page.strip("/").split("/")[-1], "unknown", "-", page, ex,
                   "Mapped to page" if ex == "Yes" else "No page yet", 1 if ptype != "post" else 2,
                   "", role, vol[page], ptype])
    for k, *_ in ROWS:
        wb["Rank tracker"].append([k])
    wb.save(OUT / "keyword-map.xlsx")

    snap = {"_note": "Synthetic SERP data for evals.", "date": "2026-01-15", "domain": "acme-plumbing.ca",
            "keywords": {k: {"vol": next(r[1] for r in ROWS if r[0] == k), "type": t, "mix": m, "urls": u,
                             "features": ["local_pack"] if "local" in t else ["people_also_ask"],
                             "related": [], "paa": [f"Is {k} worth it?"], "pg": [], "passes": 2}
                         for k, (t, m, u) in SNAP.items()}}
    (OUT / "seo-data" / "serp" / "2026-01-15.json").write_text(json.dumps(snap, indent=1), encoding="utf-8")
    with (OUT / "seo-data" / "research" / "candidates.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["keyword", "volume", "kd", "cpc", "source", "seed", "first_seen"])
        for k, v, s in CANDIDATES:
            w.writerow([k, v, "", "", s, "", "2026-01-15"])
    print(f"Built {OUT}")


if __name__ == "__main__":
    main()
