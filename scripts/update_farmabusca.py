#!/usr/bin/env python3
"""Genera farmabusca-data.json a diario a partir del CSV."""
import csv, json, os
from datetime import datetime, timezone, timedelta

OUT = "farmabusca-data.json"
CSV = "farmabusca-precios.csv"
today = (datetime.now(timezone.utc) - timedelta(hours=6)).strftime("%Y-%m-%d")

records = []
if os.path.exists(CSV):
    with open(CSV, encoding="utf-8") as f:
        lines = [l for l in f if l.strip() and not l.startswith("#")]
        if lines:
            reader = csv.DictReader(lines)
            for r in reader:
                try:
                    rec = [
                        r.get("producto","").strip(),
                        r.get("tipo","med").strip(),
                        r.get("marca","gen").strip(),
                        r.get("farmacia","").strip(),
                        r.get("direccion","").strip(),
                        r.get("telefono","").strip(),
                        r.get("ciudad","").strip(),
                        float(r.get("precio",0)),
                        r.get("moneda","NIO").strip(),
                        r.get("pais","NI").strip(),
                        r.get("departamento","").strip(),
                        today
                    ]
                    if rec[0] and rec[7] > 0:
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
print(f"FarmaBusca: {OUT} generado con {len(records)} registros.")
