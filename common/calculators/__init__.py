"""金融計算基盤モジュール

このモジュールは、各種金融計算クラスの基底となる
抽象クラスとミックスインを提供します。

Classes:
    BaseFinancialCalculator: 金融計算の抽象基底クラス
    CompoundInterestMixin: 複利計算機能を提供するミックスイン

Example:
    >>> from common.calculators.base_calculator import (
    ...     BaseFinancialCalculator,
    ...     CompoundInterestMixin
    ... )
    >>>
    >>> class MyCalculator(BaseFinancialCalculator, CompoundInterestMixin):
    ...     def calculate(self, principal, rate, years):
    ...         return self.calculate_compound_interest(principal, rate, years)
"""

__all__ = [
    "BaseFinancialCalculator",
    "CompoundInterestMixin",
]


# 遅延インポート（循環依存回避）
def __getattr__(name: str):
    if name == "BaseFinancialCalculator":
        from .base_calculator import BaseFinancialCalculator

        return BaseFinancialCalculator
    elif name == "CompoundInterestMixin":
        from .base_calculator import CompoundInterestMixin

        return CompoundInterestMixin
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
