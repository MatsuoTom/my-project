"""金融プランの基底データクラス

このモジュールは、保険プラン、年金プラン等の
金融プランに共通するデータ構造を提供します。

Classes:
    FinancialPlan: 金融プランの基底データクラス

Example:
    >>> from common.models.financial_plan import FinancialPlan
    >>>
    >>> # 30歳から60歳までの定期保険
    >>> plan = FinancialPlan(
    ...     name="定期保険",
    ...     start_age=30,
    ...     end_age=60,
    ...     annual_payment=100000
    ... )
    >>>
    >>> print(f"プラン名: {plan.name}")
    プラン名: 定期保険
    >>> print(f"期間: {plan.duration_years}年")
    期間: 30年
    >>> print(f"総支払額: {plan.total_payment:,.0f}円")
    総支払額: 3,000,000円

Author:
    my-project team

Created:
    2025-01-10 (Phase 3)
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FinancialPlan:
    """金融プランの基底データクラス

    保険プラン、年金プラン等の金融プランに共通する属性を定義します。

    Attributes:
        name: プラン名（例: "終身保険", "国民年金"）
        start_age: 開始年齢（歳）
        end_age: 終了年齢（歳、Noneの場合は終身）
        annual_payment: 年間支払額（円）

    Properties:
        duration_years: 期間（年数）
        total_payment: 総支払額（円）
        is_lifetime: 終身かどうか

    Examples:
        >>> # 30歳から60歳までの定期保険
        >>> plan = FinancialPlan(
        ...     name="定期保険",
        ...     start_age=30,
        ...     end_age=60,
        ...     annual_payment=100000
        ... )
        >>> print(plan.duration_years)
        30
        >>> print(plan.total_payment)
        3000000
        >>> print(plan.is_lifetime)
        False
        >>>
        >>> # 終身保険（終了年齢なし）
        >>> lifetime_plan = FinancialPlan(
        ...     name="終身保険",
        ...     start_age=30,
        ...     end_age=None,
        ...     annual_payment=150000
        ... )
        >>> print(lifetime_plan.is_lifetime)
        True
        >>> print(lifetime_plan.duration_years)
        None

    Raises:
        ValueError: バリデーションエラー時
            - 開始年齢が0未満
            - 終了年齢が開始年齢以下
            - 年間支払額が負

    Notes:
        - このクラスは基底クラスとして使用されることを想定しています
        - サブクラスで追加の属性や検証ロジックを実装できます
        - 不変（frozen=False）なので、属性の変更が可能です
    """

    name: str
    start_age: int
    end_age: Optional[int] = None
    annual_payment: float = 0.0

    def __post_init__(self):
        """データクラス初期化後のバリデーション

        Raises:
            ValueError: 不正な値が設定されている場合
        """
        # 開始年齢の検証
        if self.start_age < 0:
            raise ValueError(f"開始年齢は0以上である必要があります: {self.start_age}")

        # 終了年齢の検証
        if self.end_age is not None:
            if self.end_age <= self.start_age:
                raise ValueError(
                    f"終了年齢（{self.end_age}）は開始年齢（{self.start_age}）より大きい必要があります"
                )

        # 年間支払額の検証
        if self.annual_payment < 0:
            raise ValueError(f"年間支払額は0以上である必要があります: {self.annual_payment}")

    @property
    def duration_years(self) -> Optional[int]:
        """期間（年数）

        Returns:
            Optional[int]: 期間（年数）。終身の場合はNone

        Examples:
            >>> plan = FinancialPlan("定期保険", 30, 60, 100000)
            >>> print(plan.duration_years)
            30
            >>>
            >>> lifetime = FinancialPlan("終身保険", 30, None, 150000)
            >>> print(lifetime.duration_years)
            None
        """
        if self.end_age is None:
            return None
        return self.end_age - self.start_age

    @property
    def total_payment(self) -> Optional[float]:
        """総支払額（円）

        Returns:
            Optional[float]: 総支払額。終身の場合はNone

        Examples:
            >>> plan = FinancialPlan("定期保険", 30, 60, 100000)
            >>> print(plan.total_payment)
            3000000.0
            >>>
            >>> lifetime = FinancialPlan("終身保険", 30, None, 150000)
            >>> print(lifetime.total_payment)
            None

        Notes:
            - duration_years が None の場合、None を返します
            - 年間支払額 × 期間（年数）で計算します
        """
        if self.duration_years is None:
            return None
        return self.annual_payment * self.duration_years

    @property
    def is_lifetime(self) -> bool:
        """終身かどうか

        Returns:
            bool: 終身の場合 True、期間限定の場合 False

        Examples:
            >>> plan = FinancialPlan("定期保険", 30, 60, 100000)
            >>> print(plan.is_lifetime)
            False
            >>>
            >>> lifetime = FinancialPlan("終身保険", 30, None, 150000)
            >>> print(lifetime.is_lifetime)
            True
        """
        return self.end_age is None

    def __str__(self) -> str:
        """文字列表現

        Returns:
            str: プランの概要文字列

        Examples:
            >>> plan = FinancialPlan("定期保険", 30, 60, 100000)
            >>> print(plan)
            定期保険（30歳～60歳、年間10万円、総額300万円）
            >>>
            >>> lifetime = FinancialPlan("終身保険", 30, None, 150000)
            >>> print(lifetime)
            終身保険（30歳～終身、年間15万円）
        """
        if self.is_lifetime:
            return (
                f"{self.name}（{self.start_age}歳～終身、"
                f"年間{self.annual_payment/10000:.0f}万円）"
            )
        else:
            return (
                f"{self.name}（{self.start_age}歳～{self.end_age}歳、"
                f"年間{self.annual_payment/10000:.0f}万円、"
                f"総額{self.total_payment/10000:.0f}万円）"
            )

    def __repr__(self) -> str:
        """デバッグ用文字列表現

        Returns:
            str: デバッグ用の詳細文字列

        Examples:
            >>> plan = FinancialPlan("定期保険", 30, 60, 100000)
            >>> repr(plan)
            "FinancialPlan(name='定期保険', start_age=30, end_age=60, annual_payment=100000.0)"
        """
        return (
            f"FinancialPlan("
            f"name={self.name!r}, "
            f"start_age={self.start_age}, "
            f"end_age={self.end_age}, "
            f"annual_payment={self.annual_payment}"
            f")"
        )


# モジュールレベルのエクスポート
__all__ = [
    "FinancialPlan",
]
