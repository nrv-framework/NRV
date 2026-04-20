# Pytest Test Suite

This directory contains the new pytest-based test suite for NRV.

The legacy developer-oriented scripts in `tests/` remain unchanged in `tests/sciences` and are still
the scientific reference suite. The goal of `tests/` is different:

- provide CI/CD-friendly tests
- separate tests into `unit`, `e2e`, and `deployment`
- avoid COMSOL coverage in the new pytest suite

## Families

- `unit/`: small, fast, API-focused tests
- `e2e/`: strategic workflow tests with limited computational cost
- `deployment/`: environment and runtime sanity checks

## Running Tests

Run all pytest tests:

```bash
pytest tests
```

Run a specific family by path:

```bash
pytest tests/unit
pytest tests/e2e
pytest tests/deployment
```

Run a specific family by marker:

```bash
pytest -m unit
pytest -m e2e
pytest -m deployment
```

Run only FEniCS-oriented tests:

```bash
pytest -m fenics
```

Skip slower checks:

```bash
pytest -m "not slow"
```

## Environment

The project already defines pytest in the `dev` extra from `pyproject.toml`.

Typical setup:

```bash
mamba env create -n nrv-env -f conda/nrvdev.yaml
mamba activate nrv-env
```

On an existing NRV environment, only the editable install with dev extras should
be needed:

```bash
pip install -e ".[dev]"
```
