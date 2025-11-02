"""共通基盤パッケージ

このパッケージは、life_insuranceとpension_calcモジュール間で
共有される共通機能を提供します。

Modules:
    calculators: 金融計算の基底クラスとミックスイン
    models: 金融プランの基底データクラス
    utils: 数学・日付計算ユーティリティ

Example:
    >>> from common.calculators.base_calculator import BaseFinancialCalculator
    >>> from common.models.financial_plan import FinancialPlan
    >>> from common.utils.math_utils import calculate_compound_interest
"""

__version__ = "0.1.0"
__author__ = "my-project team"

__all__ = [
    # バージョン情報
    "__version__",
    "__author__",
]
