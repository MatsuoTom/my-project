"""共通ユーティリティモジュール

このモジュールは、数学計算、日付計算等の
汎用的なユーティリティ関数を提供します。

Modules:
    math_utils: 複利計算、年金現価、IRR等の数学関数
    date_utils: 年齢計算、期間計算、和暦変換等の日付関数

Example:
    >>> from common.utils.math_utils import calculate_compound_interest
    >>> from common.utils.date_utils import calculate_age
    >>>
    >>> future_value = calculate_compound_interest(1000000, 0.03, 10)
    >>> print(f"10年後: {future_value:,.0f}円")
    10年後: 1,343,916円
"""

__all__ = [
    # math_utils
    "calculate_compound_interest",
    "calculate_present_value",
    "calculate_annuity_present_value",
    "calculate_annuity_future_value",
    "calculate_irr",
    "calculate_npv",
    # date_utils
    "calculate_age",
    "calculate_years_between",
    "to_wareki",
    "from_wareki",
]


# 遅延インポート（循環依存回避）
def __getattr__(name: str):
    # math_utils
    if name in [
        "calculate_compound_interest",
        "calculate_present_value",
        "calculate_annuity_present_value",
        "calculate_annuity_future_value",
        "calculate_irr",
        "calculate_npv",
    ]:
        from .math_utils import (
            calculate_compound_interest,
            calculate_present_value,
            calculate_annuity_present_value,
            calculate_annuity_future_value,
            calculate_irr,
            calculate_npv,
        )

        return locals()[name]

    # date_utils
    elif name in ["calculate_age", "calculate_years_between", "to_wareki", "from_wareki"]:
        from .date_utils import (
            calculate_age,
            calculate_years_between,
            to_wareki,
            from_wareki,
        )

        return locals()[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
