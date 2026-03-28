# PowerShell test runner script for my-project
# Usage: .\run_tests.ps1 [fast|cov|cov-html]

param(
    [Parameter(Position=0)]
    [ValidateSet("fast", "cov", "cov-html", "")]
    [string]$Mode = ""
)

$venvPython = "C:/Users/tomma/Documents/python-projects/my-project/.venv/Scripts/python.exe"

function Show-Help {
    Write-Host "Usage: .\run_tests.ps1 [mode]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Modes:" -ForegroundColor Yellow
    Write-Host "  (none)    - Run all tests with coverage (default)"
    Write-Host "  fast      - Run tests quickly without coverage"
    Write-Host "  cov       - Run tests with coverage (skip covered files)"
    Write-Host "  cov-html  - Run tests with HTML coverage report"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  .\run_tests.ps1          # Run with coverage"
    Write-Host "  .\run_tests.ps1 fast     # Quick test"
    Write-Host "  .\run_tests.ps1 cov-html # Generate HTML report"
}

switch ($Mode) {
    "fast" {
        Write-Host "Running fast tests (no coverage)..." -ForegroundColor Green
        & $venvPython -m pytest --tb=line -q
    }
    "cov" {
        Write-Host "Running tests with coverage..." -ForegroundColor Green
        & $venvPython -m pytest --cov=life_insurance --cov=pension_calc --cov-report=term:skip-covered --tb=line -q
    }
    "cov-html" {
        Write-Host "Running tests with HTML coverage report..." -ForegroundColor Green
        & $venvPython -m pytest --cov=life_insurance --cov=pension_calc --cov-report=html --cov-report=term:skip-covered --tb=line -q
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`nCoverage report generated: htmlcov\index.html" -ForegroundColor Cyan
            Write-Host "Opening in browser..." -ForegroundColor Cyan
            Start-Process "htmlcov\index.html"
        }
    }
    "" {
        Write-Host "Running tests with coverage (default)..." -ForegroundColor Green
        & $venvPython -m pytest --cov=life_insurance --cov=pension_calc --cov-report=term:skip-covered --tb=line -q
    }
    default {
        Show-Help
        exit 1
    }
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "`n✗ Some tests failed." -ForegroundColor Red
    exit $LASTEXITCODE
}
