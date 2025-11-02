"""
生命保険プランのデータモデル

このモジュールは生命保険プランの設定を管理するデータクラスを提供します。
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class InsurancePlan:
    """
    生命保険プランの設定
    
    Attributes:
        monthly_premium: 月額保険料（円）
        annual_rate: 年間運用利回り（%表記: 例 2.0 = 2%）
        investment_period: 投資期間（年）
        fee_rate: 積立手数料率（例: 0.013 = 1.3%）
        balance_fee_rate: 残高手数料率（月次、例: 0.00008 = 0.008%/月）
        withdrawal_fee_rate: 解約手数料率（例: 0.01 = 1%）
    
    Examples:
        >>> plan = InsurancePlan(
        ...     monthly_premium=30000,
        ...     annual_rate=2.0,
        ...     investment_period=20
        ... )
        >>> plan.annual_premium
        360000
        >>> plan.total_months
        240
        >>> plan.monthly_rate
        0.001666...
    """
    
    monthly_premium: float
    annual_rate: float
    investment_period: int
    fee_rate: float = 0.013
    balance_fee_rate: float = 0.00008
    withdrawal_fee_rate: float = 0.01
    
    def __post_init__(self):
        """バリデーション"""
        if self.monthly_premium <= 0:
            raise ValueError("月額保険料は正の値である必要があります")
        if self.investment_period <= 0:
            raise ValueError("投資期間は正の値である必要があります")
        if not 0 <= self.fee_rate < 1:
            raise ValueError("積立手数料率は0以上1未満である必要があります")
        if not 0 <= self.balance_fee_rate < 1:
            raise ValueError("残高手数料率は0以上1未満である必要があります")
        if not 0 <= self.withdrawal_fee_rate < 1:
            raise ValueError("解約手数料率は0以上1未満である必要があります")
    
    @property
    def annual_premium(self) -> float:
        """年間保険料（円）"""
        return self.monthly_premium * 12
    
    @property
    def total_months(self) -> int:
        """総月数"""
        return self.investment_period * 12
    
    @property
    def monthly_rate(self) -> float:
        """月次運用利回り（小数表記）"""
        return self.annual_rate / 100 / 12
    
    @property
    def net_monthly_premium(self) -> float:
        """手数料控除後の月額保険料（円）"""
        return self.monthly_premium * (1 - self.fee_rate)
    
    def to_dict(self) -> dict:
        """辞書形式に変換（既存コードとの互換性用）"""
        return {
            'monthly_premium': self.monthly_premium,
            'annual_rate': self.annual_rate,
            'investment_period': self.investment_period,
            'fee_rate': self.fee_rate,
            'balance_fee_rate': self.balance_fee_rate,
            'withdrawal_fee_rate': self.withdrawal_fee_rate,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'InsurancePlan':
        """辞書形式から作成（既存コードとの互換性用）"""
        return cls(
            monthly_premium=data['monthly_premium'],
            annual_rate=data['annual_rate'],
            investment_period=data['investment_period'],
            fee_rate=data.get('fee_rate', 0.013),
            balance_fee_rate=data.get('balance_fee_rate', 0.00008),
            withdrawal_fee_rate=data.get('withdrawal_fee_rate', 0.01),
        )
