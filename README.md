# CC63D — Lab 4: arma tu pipeline de CI en GitHub Actions

Cuarto laboratorio del curso **CC63D — Arquitecturas de Servicios, DevOps, SRE y Cloud** (FCFM, Universidad de Chile, 2026).

Este repo trae el **monolito** instrumentado del [Lab 3](https://github.com/lnds/cc63d-lab-3) (Flask + SQLite) con una **suite de pruebas completa** (12 tests). El código y los tests **ya están hechos**.

Tu tarea es **armar la pipeline de Integración Continua** que ejecuta esas pruebas en **GitHub Actions** — el mismo patrón que viste en clase con el ejemplo en Go ([`cc63d-ci-demo`](https://github.com/lnds/cc63d-ci-demo)), pero aquí en Python.

## 🎯 El ejercicio (tarea con nota)

1. **Haz un fork** de este repo a tu cuenta de GitHub.
2. **Crea** `.github/workflows/ci.yml` con las etapas de la pipeline (ver abajo).
3. **Deja un run rojo**: haz un cambio que **rompa una prueba**, `commit` y `push` → el run de Actions falla 🔴.
4. **Déjalo verde**: **restaura** el cambio, `commit` y `push` → el run pasa 🟢.
5. **Entrega** el enlace a tu fork. **No borres los runs**: el rojo y el verde se revisan.

### Las etapas que debe tener tu `ci.yml`

| Etapa | Qué hace | Comando |
|-------|----------|---------|
| **preparar** | entorno + dependencias | `actions/setup-python` + `pip install -r requirements-dev.txt` |
| **test** | correr las pruebas (el corazón) | `pytest` |
| *(lint)* | estilo y errores estáticos (opcional) | `ruff check .` |

> Es el mismo patrón del ejemplo Go: cambia `setup-go`/`go test` por `setup-python`/`pytest`. La estructura (`on`, `jobs`, `steps`, `run`) es idéntica. En `make ci` tienes los comandos exactos.

### Criterios de aceptación

1. Tu fork tiene `.github/workflows/ci.yml` con una **etapa de test** que ejecuta `pytest`.
2. En la pestaña *Actions* de tu fork quedan **dos runs visibles**: uno **rojo** (rompiste una prueba) y uno **verde** (lo restauraste).
3. Los runs **no están borrados** y el `ci.yml` corre en `push`.
4. Respondes las preguntas de testing (abajo).

## 📝 Entrega y defensa

Entregas **dos** cosas:

1. El enlace a **tu fork**, con los **dos runs** visibles en *Actions* (🔴 y 🟢) — **sin borrarlos**.
2. Una **justificación breve** (≈ media plana), **sobre las pruebas**:

   - ¿Qué diferencia una prueba **unitaria** de una de **integración**? Señala un ejemplo de cada una en `tests/`.
   - ¿Por qué la **pirámide de pruebas** tiene muchas unitarias y pocas de extremo a extremo?
   - ¿Qué hace la fixture `client` del `conftest.py`? ¿Por qué cada prueba usa una **base de datos limpia**?
   - Una prueba puede "cubrir líneas" sin verificar comportamiento. ¿Cómo sabes que **realmente** prueba algo?
   - ¿Por qué la **etapa de test** va **antes** del build (o del deploy) en la pipeline?

> La nota pondera **que entiendas las pruebas y la pipeline**, no solo que el run quede verde.

## 🚀 Correr las pruebas localmente

```bash
make install   # instala pytest + ruff
make test      # pytest -v   (las 12 pruebas que ya vienen)
make lint      # ruff check .
make ci        # lint + test, lo mismo que debe correr tu pipeline
```

## 🧪 Las pruebas que ya vienen

| Nivel | Archivo | Qué prueba |
|-------|---------|-----------|
| Unitarias | `tests/test_reglas.py` | reglas de negocio, una invariante cada una (severidad 1-4, post-mortem requiere resuelto, servicio único…) |
| Integración | `tests/test_integracion.py` | flujo completo de punta a punta + `/health` + `/metrics` |

La fixture del `conftest.py` da a cada prueba una base de datos SQLite **temporal y limpia**, para que no dependan del orden ni se ensucien entre sí.

## 📁 Estructura del repo

```
.
├── app.py                  # monolito Flask + SQLite, instrumentado (Clase 4) — NO se toca
├── tests/                  # ✓ suite completa (12 pruebas) — NO se toca
│   ├── conftest.py
│   ├── test_reglas.py
│   └── test_integracion.py
├── ruff.toml, pytest.ini, requirements-dev.txt
├── Dockerfile, compose.yaml, Makefile
└── (observabilidad de la Clase 4: prometheus/, grafana/, error_budget.py)

  ← tú agregas:  .github/workflows/ci.yml
```

## 💡 Dónde buscar

- El ejemplo completo en Go: [`cc63d-ci-demo`](https://github.com/lnds/cc63d-ci-demo) y la *anatomía de un workflow* de la teoría.
- GitHub Actions — `docs.github.com/actions` (`jobs`, `steps`, `run`, `actions/setup-python`).
- pytest — `docs.pytest.org`.
