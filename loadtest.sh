#!/bin/bash
# ============================================================================
#  loadtest.sh — genera tráfico contra el monolito para ver los SLIs en vivo
# ============================================================================
#
#  Pega una mezcla de requests al endpoint /work (que falla ~5% de las veces)
#  y a endpoints reales. Mira el dashboard de Grafana mientras corre.
#
#  Uso:
#     bash loadtest.sh                  # 500 requests contra http://localhost:8000
#     bash loadtest.sh 1000             # 1000 requests
#     bash loadtest.sh 1000 http://localhost:8000
# ============================================================================

REQUESTS="${1:-500}"
BASE_URL="${2:-http://localhost:8000}"

echo "Generando $REQUESTS requests contra $BASE_URL ..."
echo "(abre el dashboard de Grafana en http://localhost:3001 para verlo en vivo)"

ok=0
err=0
for i in $(seq 1 "$REQUESTS"); do
  # 70% al endpoint flaky (genera las fallas), 30% a listar servicios (tráfico real)
  if [ $((RANDOM % 10)) -lt 7 ]; then
    code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/work")
  else
    code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/services")
  fi

  if [ "$code" -ge 500 ]; then
    err=$((err + 1))
  else
    ok=$((ok + 1))
  fi

  sleep 0.02

  if [ $((i % 50)) -eq 0 ]; then
    echo "  $i/$REQUESTS  (ok=$ok  err=$err)"
  fi
done

echo ""
echo "Listo. Total: $((ok + err))  ok=$ok  err=$err"
echo "Disponibilidad observada: $(python3 -c "print(f'{100*$ok/($ok+$err):.3f}%')")"
