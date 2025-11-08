"""
計算結果のデータモデル

このモジュールは保険価値計算の結果を管理するデータクラスを提供します。
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class InsuranceResult:
    """
    保険価値計算の結果

    Attributes:
        insurance_value: 保険価値（円）
        total_paid: 総払込額（円）
        total_fees: 総手数料（円）
        tax_savings: 節税額（円）
        net_value: 正味価値（円）
        return_rate: 実質利回り（%表記）
        timeline: 年次推移データ（オプション）
        breakdown: 内訳データ（オプション）

        # Phase 2拡張フィールド（コアメソッド用）
        reinvestment_value: 再投資残高（円、部分解約・乗り換え戦略用）
        setup_fee: 積立手数料（円）
        balance_fee: 残高手数料（円）
        tax_benefit: 節税効果（円、tax_savingsのエイリアス）
        surrender_value: 解約返戻金（円）
        withdrawal_tax: 解約所得税（円）
        reinvestment_tax: 再投資課税（円）
        total_return_rate: 総リターン率（%）
        actual_return_rate: 実質利回り（年率%、return_rateのエイリアス）

    Examples:
        >>> result = InsuranceResult(
        ...     insurance_value=7500000,
        ...     total_paid=7200000,
        ...     total_fees=250000,
        ...     tax_savings=500000,
        ...     net_value=7750000,
        ...     return_rate=2.5
        ... )
        >>> result.profit
        550000.0
        >>> result.profit_rate
        7.638888888888889
    """

    insurance_value: float
    total_paid: float
    total_fees: float
    tax_savings: float
    net_value: float
    return_rate: float
    timeline: Optional[List[Dict[str, Any]]] = None
    breakdown: Optional[Dict[str, Any]] = None

    # Phase 2拡張フィールド（オプション）
    reinvestment_value: float = 0.0
    setup_fee: float = 0.0
    balance_fee: float = 0.0
    tax_benefit: float = 0.0
    surrender_value: float = 0.0
    withdrawal_tax: float = 0.0
    reinvestment_tax: float = 0.0
    total_return_rate: float = 0.0
    actual_return_rate: float = 0.0

    def __post_init__(self):
        """計算値の検証"""
        if self.total_paid < 0:
            raise ValueError("総払込額は0以上である必要があります")
        if self.total_fees < 0:
            raise ValueError("総手数料は0以上である必要があります")

    @property
    def profit(self) -> float:
        """利益（円）= 正味価値 - 総払込額"""
        return self.net_value - self.total_paid

    @property
    def profit_rate(self) -> float:
        """利益率（%）"""
        if self.total_paid == 0:
            return 0.0
        return (self.profit / self.total_paid) * 100

    @property
    def gross_value(self) -> float:
        """総価値（手数料・税金控除前）"""
        return self.insurance_value + self.total_fees

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "insurance_value": self.insurance_value,
            "total_paid": self.total_paid,
            "total_fees": self.total_fees,
            "tax_savings": self.tax_savings,
            "net_value": self.net_value,
            "return_rate": self.return_rate,
            "profit": self.profit,
            "profit_rate": self.profit_rate,
            "timeline": self.timeline,
            "breakdown": self.breakdown,
        }


@dataclass
class SwitchingResult:
    """
    乗り換え戦略の計算結果

    Attributes:
        insurance_value: 保険期間の価値（円）
        insurance_tax_savings: 保険期間の節税額（円）
        fund_value: 投資信託期間の価値（円）
        total_value: 総価値（円）
        tax: 支払税金（円）
        switch_year: 乗り換え年
    """

    insurance_value: float
    insurance_tax_savings: float
    fund_value: float
    total_value: float
    tax: float
    switch_year: int

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "insurance_value": self.insurance_value,
            "insurance_tax_savings": self.insurance_tax_savings,
            "fund_value": self.fund_value,
            "total_value": self.total_value,
            "tax": self.tax,
            "switch_year": self.switch_year,
        }


@dataclass
class PartialWithdrawalResult:
    """
    部分解約戦略の計算結果

    Attributes:
        remaining_insurance: 残存保険価値（円）
        reinvestment_value: 再投資価値（円）
        tax_savings: 節税額（円）
        total_fees: 総手数料（円）
        total_value: 総価値（円）
        final_ratio: 最終残存割合
        withdrawal_years: 解約実行年のリスト
    """

    remaining_insurance: float
    reinvestment_value: float
    tax_savings: float
    total_fees: float
    total_value: float
    final_ratio: float
    withdrawal_years: List[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "remaining_insurance": self.remaining_insurance,
            "reinvestment_value": self.reinvestment_value,
            "tax_savings": self.tax_savings,
            "total_fees": self.total_fees,
            "total_value": self.total_value,
            "final_ratio": self.final_ratio,
            "withdrawal_years": self.withdrawal_years,
        }


@dataclass
class ComparisonResult:
    """
    投資信託との比較結果

    Attributes:
        insurance_result: 保険の計算結果
        fund_result: 投資信託の計算結果
        difference: 差額（保険 - 投資信託）
        breakeven_year: 損益分岐年（オプション）
    """

    insurance_result: InsuranceResult
    fund_result: Dict[str, float]
    difference: float
    breakeven_year: Optional[int] = None

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "insurance_result": self.insurance_result.to_dict(),
            "fund_result": self.fund_result,
            "difference": self.difference,
            "breakeven_year": self.breakeven_year,
        }
