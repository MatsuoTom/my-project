"""
分析モジュールの初期化
"""

from .national_pension import (
    NationalPensionAnalyzer,
    analyze_contribution_strategies
)

__all__ = [
    'NationalPensionAnalyzer',
    'analyze_contribution_strategies'
]