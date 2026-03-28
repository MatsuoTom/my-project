"""
車両維持費のデータモデル

基本的な維持費項目を管理するデータクラス
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional, Literal


@dataclass
class VehicleInfo:
    """車両基本情報"""
    name: str  # 車両名（例: トヨタ プリウス）
    purchase_date: date  # 購入日
    purchase_price: float  # 購入価格（円）
    vehicle_type: Literal["軽自動車", "普通車", "小型車", "大型車"] = "普通車"
    fuel_type: Literal["ガソリン", "ハイブリッド", "電気", "ディーゼル"] = "ガソリン"
    displacement: Optional[int] = None  # 排気量（cc）


@dataclass
class FuelExpense:
    """ガソリン代の記録"""
    date: date
    amount: float  # 給油量（L）
    price_per_liter: float  # 単価（円/L）
    odometer: Optional[int] = None  # 走行距離（km）
    
    @property
    def total_cost(self) -> float:
        """合計金額"""
        return self.amount * self.price_per_liter


@dataclass
class InspectionExpense:
    """車検費用の記録"""
    date: date
    inspection_fee: float  # 車検基本料（円）
    weight_tax: float  # 重量税（円）
    liability_insurance: float  # 自賠責保険（円）
    stamp_fee: float = 0.0  # 印紙代（円）
    other_fee: float = 0.0  # その他費用（円）
    
    @property
    def total_cost(self) -> float:
        """合計金額"""
        return (
            self.inspection_fee 
            + self.weight_tax 
            + self.liability_insurance 
            + self.stamp_fee 
            + self.other_fee
        )


@dataclass
class InsuranceExpense:
    """自動車保険（任意保険）の記録"""
    date: date
    insurance_type: Literal["年払い", "月払い"] = "年払い"
    premium: float = 0.0  # 保険料（円）
    coverage_start: Optional[date] = None  # 補償開始日
    coverage_end: Optional[date] = None  # 補償終了日


@dataclass
class TaxExpense:
    """自動車税の記録"""
    date: date
    tax_amount: float  # 税額（円）
    tax_type: Literal["自動車税", "軽自動車税"] = "自動車税"


@dataclass
class ParkingExpense:
    """駐車場代の記録"""
    date: date
    monthly_fee: float  # 月額料金（円）
    payment_type: Literal["月払い", "年払い"] = "月払い"


@dataclass
class MaintenanceExpense:
    """メンテナンス費用の記録"""
    date: date
    category: Literal[
        "オイル交換", 
        "タイヤ交換", 
        "バッテリー交換", 
        "洗車", 
        "修理", 
        "その他"
    ]
    cost: float  # 費用（円）
    description: str = ""  # 詳細説明
    odometer: Optional[int] = None  # 走行距離（km）


@dataclass
class ExpenseRecord:
    """維持費レコード（すべての費用をまとめて管理）"""
    vehicle_info: VehicleInfo
    fuel_expenses: list[FuelExpense] = field(default_factory=list)
    inspection_expenses: list[InspectionExpense] = field(default_factory=list)
    insurance_expenses: list[InsuranceExpense] = field(default_factory=list)
    tax_expenses: list[TaxExpense] = field(default_factory=list)
    parking_expenses: list[ParkingExpense] = field(default_factory=list)
    maintenance_expenses: list[MaintenanceExpense] = field(default_factory=list)
    
    def total_cost(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> dict[str, float]:
        """
        期間内の合計費用を計算
        
        Returns:
            各カテゴリの合計費用の辞書
        """
        def in_period(expense_date: date) -> bool:
            if start_date and expense_date < start_date:
                return False
            if end_date and expense_date > end_date:
                return False
            return True
        
        return {
            "ガソリン代": sum(e.total_cost for e in self.fuel_expenses if in_period(e.date)),
            "車検費用": sum(e.total_cost for e in self.inspection_expenses if in_period(e.date)),
            "保険料": sum(e.premium for e in self.insurance_expenses if in_period(e.date)),
            "自動車税": sum(e.tax_amount for e in self.tax_expenses if in_period(e.date)),
            "駐車場代": sum(
                e.monthly_fee if e.payment_type == "月払い" else e.monthly_fee * 12 
                for e in self.parking_expenses if in_period(e.date)
            ),
            "メンテナンス": sum(e.cost for e in self.maintenance_expenses if in_period(e.date)),
        }
