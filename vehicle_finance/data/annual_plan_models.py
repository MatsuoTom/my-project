"""
車両維持費の年間計画モデル

年間計画ベースの維持費管理
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional, Literal


@dataclass
class VehicleInfo:
    """車両基本情報"""
    name: str  # 車両名（例: トヨタ プリウス）
    ownership_start_year: int  # 所有開始年
    purchase_price: float  # 購入価格（円）
    vehicle_type: Literal["軽自動車", "普通車", "小型車", "大型車"] = "普通車"
    fuel_type: Literal["ガソリン", "ハイブリッド", "電気", "ディーゼル"] = "ガソリン"
    displacement: Optional[int] = None  # 排気量（cc）


@dataclass
class AnnualMaintenancePlan:
    """年間維持費計画"""
    
    year: int  # 計画年度
    
    # 燃料費
    annual_mileage: float = 10000.0  # 年間走行距離（km）
    fuel_efficiency: float = 15.0  # 燃費（km/L）
    fuel_price_per_liter: float = 160.0  # 燃料単価（円/L）
    
    # 車検費用（2年に1回）
    inspection_year: bool = False  # 車検実施年かどうか
    inspection_base_fee: float = 50000.0  # 車検基本料
    weight_tax: float = 32800.0  # 重量税
    liability_insurance: float = 20010.0  # 自賠責保険（2年分）
    inspection_other: float = 5000.0  # その他費用
    
    # 任意保険
    voluntary_insurance: float = 60000.0  # 年間保険料
    
    # 自動車税
    automobile_tax: float = 39500.0  # 年間自動車税
    
    # 駐車場代
    monthly_parking_fee: float = 10000.0  # 月額駐車場代
    
    # 定期メンテナンス
    oil_change_count: int = 2  # オイル交換回数（年間）
    oil_change_cost: float = 5000.0  # オイル交換1回あたりの費用
    tire_change: bool = False  # タイヤ交換の有無
    tire_change_cost: float = 60000.0  # タイヤ交換費用
    other_maintenance: float = 20000.0  # その他メンテナンス費用
    
    # その他
    car_wash: float = 12000.0  # 洗車・消耗品（年間）
    unexpected_expense: float = 30000.0  # 予備費
    
    @property
    def fuel_cost(self) -> float:
        """年間燃料費"""
        fuel_consumption = self.annual_mileage / self.fuel_efficiency
        return fuel_consumption * self.fuel_price_per_liter
    
    @property
    def inspection_cost(self) -> float:
        """車検費用（該当年のみ）"""
        if not self.inspection_year:
            return 0.0
        return (
            self.inspection_base_fee
            + self.weight_tax
            + self.liability_insurance
            + self.inspection_other
        )
    
    @property
    def parking_cost(self) -> float:
        """年間駐車場代"""
        return self.monthly_parking_fee * 12
    
    @property
    def maintenance_cost(self) -> float:
        """年間メンテナンス費用"""
        oil_cost = self.oil_change_count * self.oil_change_cost
        tire_cost = self.tire_change_cost if self.tire_change else 0.0
        return oil_cost + tire_cost + self.other_maintenance
    
    @property
    def total_annual_cost(self) -> float:
        """年間維持費合計"""
        return (
            self.fuel_cost
            + self.inspection_cost
            + self.voluntary_insurance
            + self.automobile_tax
            + self.parking_cost
            + self.maintenance_cost
            + self.car_wash
            + self.unexpected_expense
        )
    
    @property
    def monthly_average_cost(self) -> float:
        """月平均維持費"""
        return self.total_annual_cost / 12
    
    def breakdown(self) -> dict[str, float]:
        """費用の内訳"""
        return {
            "燃料費": self.fuel_cost,
            "車検費用": self.inspection_cost,
            "任意保険": self.voluntary_insurance,
            "自動車税": self.automobile_tax,
            "駐車場代": self.parking_cost,
            "メンテナンス": self.maintenance_cost,
            "洗車・消耗品": self.car_wash,
            "予備費": self.unexpected_expense,
        }


@dataclass
class ActualExpense:
    """実績費用（年度ごと）"""
    year: int  # 年度
    fuel_cost: float = 0.0  # 実績燃料費
    inspection_cost: float = 0.0  # 実績車検費用
    insurance_cost: float = 0.0  # 実績保険料
    tax_cost: float = 0.0  # 実績自動車税
    parking_cost: float = 0.0  # 実績駐車場代
    maintenance_cost: float = 0.0  # 実績メンテナンス費用（旧：後方互換性のため残す）
    other_cost: float = 0.0  # その他実績費用
    
    # メンテナンス詳細項目（新規追加）
    oil_change_cost: float = 0.0  # 実績オイル交換費用
    tire_change_cost: float = 0.0  # 実績タイヤ交換費用
    other_maintenance_cost: float = 0.0  # その他メンテナンス費用
    
    @property
    def total_maintenance_cost(self) -> float:
        """メンテナンス費用合計（詳細がある場合は詳細を、ない場合は一括を使用）"""
        detail_total = self.oil_change_cost + self.tire_change_cost + self.other_maintenance_cost
        return detail_total if detail_total > 0 else self.maintenance_cost
    
    @property
    def total_cost(self) -> float:
        """実績合計費用"""
        return (
            self.fuel_cost
            + self.inspection_cost
            + self.insurance_cost
            + self.tax_cost
            + self.parking_cost
            + self.total_maintenance_cost
            + self.other_cost
        )


@dataclass
class VehicleMaintenancePlan:
    """車両の複数年維持費計画"""
    vehicle_info: VehicleInfo
    annual_plans: list[AnnualMaintenancePlan] = field(default_factory=list)
    actual_expenses: list[ActualExpense] = field(default_factory=list)  # 実績データ
    
    def add_year_plan(self, plan: AnnualMaintenancePlan) -> None:
        """年度計画を追加"""
        # 既存の年度があれば上書き
        for i, existing_plan in enumerate(self.annual_plans):
            if existing_plan.year == plan.year:
                self.annual_plans[i] = plan
                return
        self.annual_plans.append(plan)
        self.annual_plans.sort(key=lambda p: p.year)
    
    def get_year_plan(self, year: int) -> Optional[AnnualMaintenancePlan]:
        """特定年度の計画を取得"""
        for plan in self.annual_plans:
            if plan.year == year:
                return plan
        return None
    
    def add_actual_expense(self, actual: ActualExpense) -> None:
        """実績費用を追加"""
        # 既存の年度があれば上書き
        for i, existing in enumerate(self.actual_expenses):
            if existing.year == actual.year:
                self.actual_expenses[i] = actual
                return
        self.actual_expenses.append(actual)
        self.actual_expenses.sort(key=lambda a: a.year)
    
    def get_actual_expense(self, year: int) -> Optional[ActualExpense]:
        """特定年度の実績を取得"""
        for actual in self.actual_expenses:
            if actual.year == year:
                return actual
        return None
    
    def total_cost_range(self, start_year: int, end_year: int) -> float:
        """期間内の合計費用"""
        total = 0.0
        for plan in self.annual_plans:
            if start_year <= plan.year <= end_year:
                total += plan.total_annual_cost
        return total
    
    def lifetime_cost(self, years: int) -> dict[str, float]:
        """生涯コスト試算"""
        # 最初の年の計画をベースに推定
        if not self.annual_plans:
            return {"error": "計画データがありません"}
        
        base_plan = self.annual_plans[0]
        total = self.vehicle_info.purchase_price  # 車両本体価格
        
        for year in range(years):
            # 車検年かどうか（初回3年、以降2年ごと）
            is_inspection = (year == 2) or (year > 2 and (year - 2) % 2 == 0)
            
            # 各年の費用を計算
            annual_cost = (
                base_plan.fuel_cost
                + (base_plan.inspection_cost if is_inspection else 0)
                + base_plan.voluntary_insurance
                + base_plan.automobile_tax
                + base_plan.parking_cost
                + base_plan.maintenance_cost
                + base_plan.car_wash
                + base_plan.unexpected_expense
            )
            total += annual_cost
        
        return {
            "車両本体価格": self.vehicle_info.purchase_price,
            "維持費合計": total - self.vehicle_info.purchase_price,
            "総額": total,
            "年平均": total / years if years > 0 else 0,
            "月平均": total / (years * 12) if years > 0 else 0,
        }
