#!/bin/bash
set -e
MODE="${1:-unit}"

case "$MODE" in
    unit)
        pytest tests/unit/ -v --cov=. --cov-report=term-missing --cov-fail-under=80
        ;;
    integration)
        pytest tests/integration/ -v --tb=short
        ;;
    tenant)
        pytest tests/tenant/ -v -m tenant
        ;;
    payment)
        pytest tests/payment/ -v --run-slow
        ;;
    all)
        pytest tests/ -v --cov=. --cov-report=html
        ;;
    *)
        echo "Usage: $0 {unit|integration|tenant|payment|all}"
        exit 1
        ;;
esac
