#!/usr/bin/env python3
"""Genera repuestos-data.json a diario a partir del CSV."""
import csv, json, os
from datetime import datetime, timezone, timedelta

OUT = "repuestos-data.json"
CSV = "repuestos-precios.csv"
today = (datetime.now(timezone.utc) - timedelta(hours=6)).strftime("%Y-%m-%d")

records = []
if os.path.exists(CSV):
    with open(CSV, encoding="utf-8") as f:
        lines = [l for l in f if l.strip() and not l.startswith("#")]
        if lines:
            reader = csv.DictReader(lines)
            for r in reader:
                try:
                    rec = {
                        "id": r.get("id","").strip(),
                        "name": r.get("name","").strip(),
                        "category": r.get("category","").strip(),
                        "categoryLabel": r.get("categoryLabel","").strip(),
                        "vehicleTypes": r.get("vehicleTypes","all").split("|"),
                        "brands": r.get("brands","all").split("|"),
                        "years": r.get("years","all").split("|"),
                        "makeModel": r.get("makeModel","").strip(),
                        "description": r.get("description","").strip(),
                        "oem": r.get("oem","").strip(),
                        "priceUsd": float(r.get("priceUsd",0)),
                        "model3d": r.get("model3d","sedan").strip(),
                        "part3d": r.get("part3d","box").strip(),
                        "department": r.get("department","Managua").strip(),
                        "municipio": r.get("municipio","Managua").strip(),
                        "market": r.get("market","nacional").strip(),
                        "storeName": r.get("storeName","").strip(),
                        "storePhone": r.get("storePhone","").strip(),
                        "storeWhatsapp": r.get("storeWhatsapp","").strip()
                    }
                    if rec["name"] and rec["priceUsd"] > 0:
                        records.append(rec)
                except Exception as e:
                    print(f"Error en fila: {e}")

data = {
    "version": today.replace("-", ".") + ".1",
    "updated": today,
    "records": records
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
print(f"Repuestos: {OUT} generado con {len(records)} registros.")
