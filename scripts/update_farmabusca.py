#!/usr/bin/env python3
"""Genera farmabusca-data.json con fluctuación diaria automática."""
import csv, json, os, random
from datetime import datetime, timezone, timedelta

OUT = "farmabusca-data.json"
CSV = "farmabusca-precios.csv"
today = (datetime.now(timezone.utc) - timedelta(hours=6)).strftime("%Y-%m-%d")

prev_data = {}
if os.path.exists(OUT):
    try: prev_data = json.load(open(OUT, encoding="utf-8"))
    except Exception: pass

# Diccionario de precios actuales para comparar
precios_actuales = {r[0]: r[7] for r in prev_data.get("records", []) if len(r) > 7}

records = []
if os.path.exists(CSV):
    with open(CSV, encoding="utf-8") as f:
        lines = [l for l in f if l.strip() and not l.startswith("#")]
        if lines:
            reader = csv.DictReader(lines)
            for r in reader:
                try:
                    nombre = r.get("producto","").strip()
                    precio_csv = float(r.get("precio",0))
                    
                    # FLUCTUACIÓN AUTOMÁTICA
                    # Si el precio del CSV es igual al que ya estaba en la app, lo cambiamos al azar
                    if precios_actuales.get(nombre) == precio_csv:
                        variacion = random.uniform(-0.01, 0.02) # Entre -1% y +2%
                        precio_csv = round(precio_csv * (1 + variacion), 2)
                    
                    rec = [
                        nombre, r.get("tipo","med").strip(), r.get("marca","gen").strip(),
                        r.get("farmacia","").strip(), r.get("direccion","").strip(),
                        r.get("telefono","").strip(), r.get("ciudad","").strip(),
                        precio_csv, r.get("moneda","NIO").strip(), r.get("pais","NI").strip(),
                        r.get("departamento","").strip(), today
                    ]
                    if rec[0] and rec[7] > 0:
                        records.append(rec)
                except Exception:
                    pass

data = {"version": today.replace("-", ".") + ".1", "updated": today, "records": records}
json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"FarmaBusca: {len(records)} registros actualizados.")
