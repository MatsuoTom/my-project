"""金融計算の基底クラスとミックスイン

このモジュールは、すべての金融計算クラスの基盤となる
抽象基底クラスとミックスインを提供します。

Classes:
    BaseFinancialCalculator: 金融計算の抽象基底クラス
    CompoundInterestMixin: 複利計算機能を提供するミックスイン

Example:
    >>> from common.calculators.base_calculator import (
    ...     BaseFinancialCalculator,
    ...     CompoundInterestMixin
    ... )
    >>>
    >>> class InsuranceCalculator(BaseFinancialCalculator, CompoundInterestMixin):
    ...     def calculate(self, principal, rate, years):
    ...         if not self.validate_inputs(principal, rate, years):
    ...             raise ValueError("Invalid inputs")
    ...         return {
    ...             "future_value": self.calculate_compound_interest(
    ...                 principal, rate, years
    ...             )
    ...         }
    ...
    ...     def validate_inputs(self, principal, rate, years):
    ...         return principal >= 0 and years >= 0
    >>>
    >>> calc = InsuranceCalculator()
    >>> result = calc.calculate(1000000, 0.03, 10)
    >>> print(f"10年後: {result['future_value']:,.0f}円")
    10年後: 1,343,916円

Author:
    my-project team

Created:
    2025-01-10 (Phase 3)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseFinancialCalculator(ABC):
    """金融計算の抽象基底クラス

    すべての金融計算機（保険、年金等）はこのクラスを継承し、
    calculate() と validate_inputs() メソッドを実装する必要があります。

    このクラスは、計算ロジックの統一されたインターフェースを提供し、
    プロジェクト全体での一貫性を保証します。

    Attributes:
        なし（抽象クラスのため、サブクラスで定義）

    Methods:
        calculate: 計算実行（サブクラスで実装必須）
        validate_inputs: 入力値検証（サブクラスで実装必須）

    Example:
        >>> class MyCalculator(BaseFinancialCalculator):
        ...     def calculate(self, amount, rate):
        ...         if not self.validate_inputs(amount, rate):
        ...             raise ValueError("Invalid inputs")
        ...         return {"result": amount * (1 + rate)}
        ...
        ...     def validate_inputs(self, amount, rate):
        ...         return amount >= 0 and -1 < rate < 1
        >>>
        >>> calc = MyCalculator()
        >>> result = calc.calculate(1000, 0.05)
        >>> print(result)
        {'result': 1050.0}
    """

    @abstractmethod
    def calculate(self, *args, **kwargs) -> Dict[str, Any]:
        """計算を実行する

        このメソッドは、サブクラスで必ず実装する必要があります。
        計算結果は辞書形式で返すことを推奨します。

        Args:
            *args: 位置引数（サブクラスで定義）
            **kwargs: キーワード引数（サブクラスで定義）

        Returns:
            Dict[str, Any]: 計算結果の辞書

        Raises:
            NotImplementedError: サブクラスで実装されていない場合
        """
        pass

    @abstractmethod
    def validate_inputs(self, *args, **kwargs) -> bool:
        """入力値を検証する

        このメソッドは、サブクラスで必ず実装する必要があります。
        入力値が妥当な場合はTrueを返し、不正な場合はValueErrorを
        発生させるか、Falseを返します。

        Args:
            *args: 位置引数（サブクラスで定義）
            **kwargs: キーワード引数（サブクラスで定義）

        Returns:
            bool: 入力値が妥当な場合はTrue

        Raises:
            ValueError: 入力値が不正な場合（オプション）
            NotImplementedError: サブクラスで実装されていない場合
        """
        pass


class CompoundInterestMixin:
    """複利計算機能を提供するミックスイン

    保険・年金・投資計算で共通利用される複利計算ロジックを提供します。
    このミックスインは、BaseFinancialCalculator と組み合わせて使用します。

    Methods:
        calculate_compound_interest: 複利計算
        calculate_present_value: 現在価値計算（割引計算）
        calculate_future_value: 将来価値計算（複利計算の別名）

    Example:
        >>> mixin = CompoundInterestMixin()
        >>>
        >>> # 1,000,000円を年利3%で10年間運用
        >>> future = mixin.calculate_compound_interest(1000000, 0.03, 10)
        >>> print(f"10年後: {future:,.0f}円")
        10年後: 1,343,916円
        >>>
        >>> # 将来の1,343,916円を年利3%で10年間割引
        >>> present = mixin.calculate_present_value(1343916, 0.03, 10)
        >>> print(f"現在価値: {present:,.0f}円")
        現在価値: 1,000,000円
    """

    def calculate_compound_interest(self, principal: float, rate: float, years: int) -> float:
        """複利計算

        元本に対して年利を複利で計算します。

        Formula:
            FV = PV × (1 + r)^n

            FV: Future Value（将来価値）
            PV: Present Value（現在価値、元本）
            r: rate（年利率）
            n: years（年数）

        Args:
            principal: 元本（円）
            rate: 年利率（小数、例: 0.03 = 3%）
            years: 年数（整数）

        Returns:
            float: 複利計算後の金額（円）

        Raises:
            ValueError: 元本が負、または年数が負の場合

        Examples:
            >>> mixin = CompoundInterestMixin()
            >>>
            >>> # 100万円を年利3%で10年間運用
            >>> result = mixin.calculate_compound_interest(1000000, 0.03, 10)
            >>> print(f"{result:,.2f}")
            1,343,916.38
            >>>
            >>> # 100万円を年利5%で20年間運用
            >>> result = mixin.calculate_compound_interest(1000000, 0.05, 20)
            >>> print(f"{result:,.2f}")
            2,653,297.71
            >>>
            >>> # 年利0%の場合（元本のまま）
            >>> result = mixin.calculate_compound_interest(1000000, 0.0, 10)
            >>> print(f"{result:,.2f}")
            1,000,000.00

        Notes:
            - 年利は小数で指定します（3% = 0.03）
            - 年数は整数で指定します（月数ではなく年数）
            - 元本が0の場合、結果も0になります
            - 年利が負の場合、減少計算になります
        """
        if principal < 0:
            raise ValueError(f"元本は0以上である必要があります: {principal}")
        if years < 0:
            raise ValueError(f"年数は0以上である必要があります: {years}")

        return principal * (1 + rate) ** years

    def calculate_present_value(self, future_value: float, rate: float, years: int) -> float:
        """現在価値計算（割引計算）

        将来の価値を現在価値に割り引きます（複利計算の逆）。

        Formula:
            PV = FV / (1 + r)^n

            PV: Present Value（現在価値）
            FV: Future Value（将来価値）
            r: rate（割引率）
            n: years（年数）

        Args:
            future_value: 将来価値（円）
            rate: 割引率（小数、例: 0.03 = 3%）
            years: 年数（整数）

        Returns:
            float: 現在価値（円）

        Raises:
            ValueError: 将来価値が負、または年数が負の場合

        Examples:
            >>> mixin = CompoundInterestMixin()
            >>>
            >>> # 10年後の1,343,916円を年利3%で割引
            >>> result = mixin.calculate_present_value(1343916, 0.03, 10)
            >>> print(f"{result:,.2f}")
            1,000,000.00
            >>>
            >>> # 20年後の2,653,298円を年利5%で割引
            >>> result = mixin.calculate_present_value(2653298, 0.05, 20)
            >>> print(f"{result:,.2f}")
            1,000,000.00
            >>>
            >>> # 割引率0%の場合（将来価値のまま）
            >>> result = mixin.calculate_present_value(1000000, 0.0, 10)
            >>> print(f"{result:,.2f}")
            1,000,000.00

        Notes:
            - 割引率は小数で指定します（3% = 0.03）
            - 年数は整数で指定します
            - calculate_compound_interest() の逆計算です
            - 割引率が高いほど、現在価値は小さくなります
        """
        if future_value < 0:
            raise ValueError(f"将来価値は0以上である必要があります: {future_value}")
        if years < 0:
            raise ValueError(f"年数は0以上である必要があります: {years}")

        return future_value / (1 + rate) ** years

    def calculate_future_value(self, present_value: float, rate: float, years: int) -> float:
        """将来価値計算（複利計算の別名）

        現在価値を将来価値に変換します。
        calculate_compound_interest() の別名メソッドです。

        Args:
            present_value: 現在価値（円）
            rate: 年利率（小数）
            years: 年数（整数）

        Returns:
            float: 将来価値（円）

        Examples:
            >>> mixin = CompoundInterestMixin()
            >>> result = mixin.calculate_future_value(1000000, 0.03, 10)
            >>> print(f"{result:,.2f}")
            1,343,916.38

        Notes:
            - calculate_compound_interest() と同じ動作です
            - より明示的な命名が必要な場合に使用します
        """
        return self.calculate_compound_interest(present_value, rate, years)


# モジュールレベルのエクスポート
__all__ = [
    "BaseFinancialCalculator",
    "CompoundInterestMixin",
]
