"""
core - 生命保険料控除の計算コアモジュール

基本的な控除額計算と税額計算を提供する基盤モジュール。

モジュール:
- deduction_calculator: 旧生命保険料控除額の計算エンジン
- tax_calculator: 税額計算と節税効果分析エンジン
"""

from life_insurance.core.deduction_calculator import LifeInsuranceDeductionCalculator
from life_insurance.core.tax_calculator import TaxCalculator

__all__ = [
    "LifeInsuranceDeductionCalculator",
    "TaxCalculator",
]