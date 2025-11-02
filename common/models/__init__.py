"""金融プランデータモデルモジュール

このモジュールは、金融プラン（保険、年金等）の
共通データ構造を提供します。

Classes:
    FinancialPlan: 金融プランの基底データクラス

Example:
    >>> from common.models.financial_plan import FinancialPlan
    >>> 
    >>> plan = FinancialPlan(
    ...     name="定期保険",
    ...     start_age=30,
    ...     end_age=60,
    ...     annual_payment=100000
    ... )
    >>> print(plan.duration_years)
    30
"""

__all__ = [
    "FinancialPlan",
]

# 遅延インポート（循環依存回避）
def __getattr__(name: str):
    if name == "FinancialPlan":
        from .financial_plan import FinancialPlan
        return FinancialPlan
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
