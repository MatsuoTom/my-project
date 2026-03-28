# Makefile for my-project
# Quick test commands for development

.PHONY: test test-fast test-cov test-cov-html clean help

# Default target
help:
	@echo "Available targets:"
	@echo "  test          - Run all tests (fast, no coverage)"
	@echo "  test-fast     - Run tests without verbose output"
	@echo "  test-cov      - Run tests with coverage report (skip covered)"
	@echo "  test-cov-html - Run tests with HTML coverage report"
	@echo "  clean         - Remove test cache and coverage files"

# Fast test without coverage
test:
	pytest --tb=short -q

# Ultra-fast test (minimal output)
test-fast:
	pytest --tb=line -q

# Test with coverage (optimized)
test-cov:
	pytest --cov=life_insurance --cov=pension_calc --cov-report=term:skip-covered --tb=line -q

# Test with HTML coverage report
test-cov-html:
	pytest --cov=life_insurance --cov=pension_calc --cov-report=html --cov-report=term:skip-covered --tb=line -q
	@echo "Coverage report generated in htmlcov/index.html"

# Clean up
clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -f .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
