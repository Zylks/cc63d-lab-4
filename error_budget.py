#!/usr/bin/env python3
"""
error_budget.py — calcula el error budget a partir de las métricas reales.

Consulta a Prometheus (su HTTP API, /api/v1/query) cuántas requests hubo y
cuántas fallaron en una ventana, y traduce eso a presupuesto de error:

    Error budget = 100% - SLO

Un SLO de 99.9% te da un presupuesto de 0.1%: de cada 1000 requests, 1 puede
fallar y sigues cumpliendo. El presupuesto NO es para no usarlo: es lo que
puedes "gastar" en desplegar, experimentar y tomar riesgos.

Uso:
    python3 error_budget.py                          # SLO 99.9%, ventana 1h
    python3 error_budget.py --slo 99.95 --window 30m
    python3 error_budget.py --slo 99.9 --window 6h --prometheus http://localhost:9090

Solo usa la biblioteca estándar (urllib): no requiere instalar nada.
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request


def query(prometheus_url, expr):
    """Ejecuta una query instantánea contra la API de Prometheus."""
    url = prometheus_url.rstrip("/") + "/api/v1/query?" + urllib.parse.urlencode({"query": expr})
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.load(resp)
    if data.get("status") != "success":
        raise RuntimeError(f"Prometheus error: {data}")
    result = data["data"]["result"]
    if not result:
        return 0.0
    return float(result[0]["value"][1])


def fmt_duration(minutes):
    """Formatea minutos como '1d 2h 3m' para leerlo cómodo."""
    minutes = max(0, minutes)
    d, rem = divmod(int(round(minutes)), 60 * 24)
    h, m = divmod(rem, 60)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    parts.append(f"{m}m")
    return " ".join(parts)


def main():
    p = argparse.ArgumentParser(description="Calcula el error budget desde Prometheus")
    p.add_argument("--slo", type=float, default=99.9, help="SLO de disponibilidad en %% (default 99.9)")
    p.add_argument("--window", default="1h", help="ventana PromQL a medir (default 1h)")
    p.add_argument("--period-days", type=int, default=30, help="período del SLO en días, para el presupuesto de tiempo (default 30)")
    p.add_argument("--prometheus", default="http://localhost:9090", help="URL de Prometheus")
    args = p.parse_args()

    total = query(args.prometheus, f"sum(increase(http_requests_total[{args.window}]))")
    failed = query(args.prometheus, f'sum(increase(http_requests_total{{status=~"5.."}}[{args.window}]))')

    if total < 1:
        print(f"No hay tráfico suficiente en la ventana [{args.window}]. Corre antes: bash loadtest.sh")
        sys.exit(1)

    availability = (total - failed) / total * 100
    budget_fraction = (100 - args.slo) / 100          # fracción de fallas permitidas
    allowed_failures = total * budget_fraction         # presupuesto, en requests
    consumed_pct = (failed / allowed_failures * 100) if allowed_failures > 0 else float("inf")
    remaining_pct = 100 - consumed_pct

    # Traducción a presupuesto de TIEMPO para el período (downtime permitido)
    period_minutes = args.period_days * 24 * 60
    budget_minutes = period_minutes * budget_fraction

    print("=" * 60)
    print(f"  ERROR BUDGET  ·  SLO {args.slo}%  ·  ventana medida: {args.window}")
    print("=" * 60)
    print(f"  Requests totales        : {total:,.0f}")
    print(f"  Requests fallidas (5xx) : {failed:,.0f}")
    print(f"  Disponibilidad observada: {availability:.4f}%")
    print("-" * 60)
    print(f"  Presupuesto de error    : {budget_fraction * 100:.3f}%  ({allowed_failures:,.1f} requests)")
    print(f"  Consumido               : {consumed_pct:.1f}%  ({failed:,.0f} requests)")
    print(f"  Restante                : {remaining_pct:.1f}%")
    print("-" * 60)
    print(f"  Presupuesto de tiempo en {args.period_days} días: {fmt_duration(budget_minutes)} de downtime permitido")
    print("=" * 60)

    if remaining_pct < 0:
        print("  ⛔ Presupuesto AGOTADO: congela features, prioriza fiabilidad.")
    elif remaining_pct < 25:
        print("  ⚠️  Presupuesto casi agotado: cuidado con los despliegues riesgosos.")
    else:
        print("  ✅ Presupuesto sano: hay margen para desplegar y experimentar.")


if __name__ == "__main__":
    main()
