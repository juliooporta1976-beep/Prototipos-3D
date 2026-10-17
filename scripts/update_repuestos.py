#!/usr/bin/env python3
"""Genera repuestos-data.json con fluctuación diaria automática."""
import csv, json, os, random
from datetime import datetime, timezone, timedelta

OUT = "repuestos-data.json"
CSV = "repuestos-precios.csv"
today = (datetime.now(timezone.utc) - timedelta(hours=6)).strftime("%Y-%m-%d")

prev_data = {}
if os.path.exists(OUT):
    try: prev_data = json.load(open(OUT, encoding="utf-8"))
    except Exception: pass

# Diccionario de precios actuales para comparar
precios_actuales = {r["id"]: r["priceUsd"] for r in prev_data.get("records", [])}

records = []
if os.path.exists(CSV):
    with open(CSV, encoding="utf-8") as f:
        lines = [l for l in f if l.strip() and not l.startswith("#")]
        if lines:
            reader = csv.DictReader(lines)
            for r in reader:
                try:
                    pid = r.get("id","").strip()
                    precio_csv = float(r.get("priceUsd",0))
                    
                    # FLUCTUACIÓN AUTOMÁTICA
                    # Si el precio del CSV es igual al que ya estaba, lo cambiamos al azar
                    if precios_actuales.get(pid) == precio_csv:
                        variacion = random.uniform(-0.02, 0.03) # Entre -2% y +3%
                        precio_csv = round(precio_csv * (1 + variacion), 2)

                    rec = {
                        "id": pid, "name": r.get("name","").strip(),
                        "category": r.get("category","").strip(), "categoryLabel": r.get("categoryLabel","").strip(),
                        "vehicleTypes": r.get("vehicleTypes","all").split("|"),
                        "brands": r.get("brands","all").split("|"), "years": r.get("years","all").split("|"),
                        "makeModel": r.get("makeModel","").strip(), "description": r.get("description","").strip(),
                        "oem": r.get("oem","").strip(), "priceUsd": precio_csv,
                        "model3d": r.get("model3d","sedan").strip(), "part3d": r.get("part3d","box").strip(),
                        "department": r.get("department","Managua").strip(), "municipio": r.get("municipio","Managua").strip(),
                        "market": r.get("market","nacional").strip(), "storeName": r.get("storeName","").strip(),
                        "storePhone": r.get("storePhone","").strip(), "storeWhatsapp": r.get("storeWhatsapp","").strip()
                    }
                    if rec["name"] and rec["priceUsd"] > 0:
                        records.append(rec)
                except Exception:
                    pass

data = {"version": today.replace("-", ".") + ".1", "updated": today, "records": records}
json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"Repuestos: {len(records)} registros actualizados.")
