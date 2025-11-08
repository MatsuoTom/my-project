"""
投資信託プランのデータモデル

このモジュールは投資信託プランの設定を管理するデータクラスを提供します。
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FundPlan:
    """
    投資信託プランの設定

    Attributes:
        annual_return: 年間期待リターン（%表記: 例 5.0 = 5%）
        annual_fee: 年間実質コスト（%表記: 例 0.5 = 0.5%）
        tax_rate: キャピタルゲイン税率（例: 0.20315 = 20.315%）
        reinvestment_rate: 再投資時の年間利回り（%表記）
        use_nisa: NISA枠を使用するか（非課税）

    Examples:
        >>> fund = FundPlan(annual_return=5.0, annual_fee=0.5)
        >>> fund.net_return
        4.5
        >>> fund.monthly_return
        0.375
        >>> fund.monthly_return_rate
        0.00375
        >>> # 再投資用
        >>> fund2 = FundPlan(reinvestment_rate=5.0, use_nisa=True)
        >>> fund2.reinvestment_rate
        5.0
    """

    annual_return: float = 0.0
    annual_fee: float = 0.0
    tax_rate: float = 0.20315  # 20.315%（所得税15.315% + 住民税5%）
    reinvestment_rate: float = 0.0  # 再投資用の年間利回り（%）
    use_nisa: bool = False  # NISA枠利用フラグ

    def __post_init__(self):
        """バリデーション"""
        # annual_feeが設定されている場合のみチェック
        if self.annual_fee != 0.0 and self.annual_fee < 0:
            raise ValueError("年間コストは0以上である必要があります")
        if not 0 <= self.tax_rate <= 1:
            raise ValueError("税率は0以上1以下である必要があります")
        # reinvestment_rateが設定されていればannual_returnとして使用
        if self.reinvestment_rate != 0.0 and self.annual_return == 0.0:
            self.annual_return = self.reinvestment_rate

    @property
    def net_return(self) -> float:
        """手数料控除後の年間リターン（%表記）"""
        return self.annual_return - self.annual_fee

    @property
    def monthly_return(self) -> float:
        """手数料控除後の月次リターン（%表記）"""
        return self.net_return / 12

    @property
    def monthly_return_rate(self) -> float:
        """月次リターン（小数表記）"""
        return self.monthly_return / 100

    @property
    def annual_return_rate(self) -> float:
        """年間期待リターン（小数表記）"""
        return self.annual_return / 100

    @property
    def net_return_rate(self) -> float:
        """手数料控除後の年間リターン（小数表記）"""
        return self.net_return / 100

    def to_dict(self) -> dict:
        """辞書形式に変換（既存コードとの互換性用）"""
        return {
            "annual_return": self.annual_return,
            "annual_fee": self.annual_fee,
            "tax_rate": self.tax_rate,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FundPlan":
        """辞書形式から作成（既存コードとの互換性用）"""
        return cls(
            annual_return=data["annual_return"],
            annual_fee=data["annual_fee"],
            tax_rate=data.get("tax_rate", 0.20315),
        )
