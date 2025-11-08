"""
生命保険モジュール用のデータモデル

このパッケージには保険計算に使用されるデータクラスが含まれます。
"""

from .insurance_plan import InsurancePlan
from .fund_plan import FundPlan
from .calculation_result import InsuranceResult

__all__ = [
    "InsurancePlan",
    "FundPlan",
    "InsuranceResult",
]
