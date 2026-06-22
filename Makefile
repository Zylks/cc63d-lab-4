# ============================================================================
#  Makefile — flujo del laboratorio de CI/CD (Clase 5, monolito)
# ============================================================================
#  El SRE automatiza el toil: en vez de recordar comandos largos, los nombramos.
#
#   --- CI: calidad automática ---
#     make install      instala dependencias de desarrollo (pytest, ruff)
#     make lint         corre el linter (ruff)
#     make test         corre la suite de pruebas (pytest)
#     make ci           lint + test (lo mismo que debe correr tu pipeline)
#
#   --- App + observabilidad (de la Clase 4) ---
#     make up           levanta la plataforma (app + Prometheus + Grafana)
#     make down         para todo (conserva los datos)
#     make clean        para todo y borra los volúmenes (datos incluidos)
#     make logs         sigue los logs de la app
#     make seed         carga datos de ejemplo
#     make loadtest     genera tráfico para ver los SLIs en movimiento
#     make error-budget calcula el error budget desde Prometheus (SLO=99.9)
# ============================================================================

SLO ?= 99.9
WINDOW ?= 1h

.PHONY: install lint test ci up down clean logs seed loadtest error-budget ps urls

install:
	pip install -r requirements-dev.txt

lint:
	ruff check .

test:
	pytest -v

ci: lint test          ## lo mismo que debe correr tu pipeline de GitHub Actions

up:
	docker compose up --build -d
	@$(MAKE) urls

down:
	docker compose down

clean:
	docker compose down -v

logs:
	docker compose logs -f app

ps:
	docker compose ps

seed:
	bash seed.sh http://localhost:8000

loadtest:
	bash loadtest.sh

error-budget:
	python3 error_budget.py --slo $(SLO) --window $(WINDOW)

urls:
	@echo ""
	@echo "  App        ->  http://localhost:8000"
	@echo "  Métricas   ->  http://localhost:8000/metrics"
	@echo "  Prometheus ->  http://localhost:9090"
	@echo "  Grafana    ->  http://localhost:3001   (admin / admin)"
	@echo ""
