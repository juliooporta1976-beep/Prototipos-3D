#!/usr/bin/env python3
"""Aplica las mejoras a MercaNica.html (idempotente: se puede correr varias veces)."""
import re, sys
from datetime import datetime, timedelta, timezone

F = sys.argv[1] if len(sys.argv) > 1 else "MercaNica.html"
h = open(F, encoding="utf-8").read()
today = (datetime.now(timezone.utc) - timedelta(hours=6)).strftime("%Y-%m-%d")

R = [
  ('<  <div style="background:linear-gradient(135deg,rgba(6,182,212',
   '<div style="background:linear-gradient(135deg,rgba(6,182,212'),
  ('autoUpdateMs: 30 * 60 * 1000,',
   'autoUpdateMs: 30 * 60 * 1000,\n  dataUrl: "mercanica-data.json",'),
  ('let r = CFG.bcn[y];', 'let r = (DATA.fx && DATA.fx.USD) || CFG.bcn[y];'),
  ('p2:"🌎 3 idiomas"', 'p2:"🌎 Español e inglés"'),
  ('p2:"🌎 3 languages"', 'p2:"🌎 Spanish & English"'),
  ('p4:"💱 13 monedas"', 'p4:"💱 C$ y USD"'),
  ('p4:"💱 13 currencies"', 'p4:"💱 C$ & USD"'),
  ('covH:"ℹ️ Cobertura y avisos"}',
   'covH:"ℹ️ Cobertura y avisos",noneTitle:"No encontramos ese producto",noneSub:"Prueba con otra palabra o pídelo abajo y lo agregamos.",updAt:"Datos al",updDone:"✅ Precios actualizados"}'),
  ('covH:"ℹ️ Coverage and notices"}',
   'covH:"ℹ️ Coverage and notices",noneTitle:"We could not find that product",noneSub:"Try another word or request it below.",updAt:"Data as of",updDone:"✅ Prices updated"}'),
  ('· «${esc(q)}»</span></div>',
   '· «${esc(q)}» · ${esc(t("updAt"))} ${esc(DATA.updated||"")}</span></div>'),
  ('new Date("2026-10-01T00:00:00Z")', 'new Date("2026-10-01T11:15:00Z")'),
  ('box.innerHTML = `<span class="dot"></span> <span>${esc(t("updNext"))}</span> `+',
   'box.innerHTML = `<span class="dot"></span> <span>${esc(t("updAt"))} <b>${esc(DATA.updated||"—")}</b> · </span><span>${esc(t("updNext"))}</span> `+'),
  ('if(j && j.products && j.stores && j.basePrices){',
   'if(j && j.products && j.stores && j.basePrices && (j.updated||"") >= (DATA.updated||"") && !(j.version===DATA_VERSION && j.updated===DATA.updated)){'),
  ('resetCaches(); prepData();',
   'resetCaches(); prepData(); setTimeout(function(){ showToast(\'<div class="ok">\'+esc(t("updDone"))+\'</div>\', 3000); }, 50);'),
  ("const C = 'mercanica-v2';", "const C = 'mercanica-v3';"),
  ('Los datos que nos proporcionas son solo para contactarte.',
   'Los datos que nos proporcionas son solo para contactarte. El número de referencia de tu depósito se envía a nuestro verificador de pagos (Google Apps Script) únicamente para activar tu acceso. Tus reportes y preferencias se guardan solo en tu dispositivo.'),
  ('Los precios mostrados son finales, sin tarifas ocultas.',
   'El pase tiene un costo único de USD 3 por 30 días, sin tarifas ocultas. Los precios de productos son estimaciones de referencia, no ofertas de las tiendas.'),
  ('MercaNica es una plataforma de demostración. Al no procesar pagos directamente en esta versión, no aplican reembolsos. Si en el futuro se integran pasarelas de pago, se detallará aquí la política de devoluciones.',
   'El pase de 30 días (USD 3) se paga por depósito bancario y se activa al verificar tu número de referencia. Si pagaste y no logras activarlo en 48 horas, escríbenos con tu comprobante y lo resolvemos o te reembolsamos. Una vez activado y usado el acceso, no hay reembolso por cambio de opinión.'),
]

for old, new in R:
    if old in h:
        h = h.replace(old, new, 1); print("OK       ", old[:55].replace("\n", " "))
    elif new in h:
        print("ya hecho ", old[:55].replace("\n", " "))
    else:
        print("NO ENCONTRADO (revisar a mano):", old[:55].replace("\n", " "))

h = re.sub(r'(<meta name="app-version" content=")[^"]*',
           r'\g<1>%s.1' % today.replace("-", "."), h, 1)
h = re.sub(r'("version":")[^"]*(","currency":"NIO","updated":")[^"]*',
           r'\g<1>%s.1\g<2>%s' % (today.replace("-", "."), today), h, 1)
open(F, "w", encoding="utf-8").write(h)
print("patch aplicado a", F)
