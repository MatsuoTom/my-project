"""
車両維持費の実績トラッカー

データの追加・保存・読み込み機能を提供
"""

import json
import pickle
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from vehicle_finance.data.models import (
    ExpenseRecord,
    VehicleInfo,
    FuelExpense,
    InspectionExpense,
    InsuranceExpense,
    TaxExpense,
    ParkingExpense,
    MaintenanceExpense,
)


class ExpenseTracker:
    """維持費トラッカー"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        初期化
        
        Args:
            data_dir: データ保存ディレクトリ（Noneの場合はデフォルト）
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data" / "saved_data"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.records: dict[str, ExpenseRecord] = {}  # 車両名 -> ExpenseRecord
    
    def add_vehicle(self, vehicle_info: VehicleInfo) -> None:
        """
        車両を追加
        
        Args:
            vehicle_info: 車両情報
        """
        if vehicle_info.name in self.records:
            raise ValueError(f"車両 '{vehicle_info.name}' は既に登録されています")
        
        self.records[vehicle_info.name] = ExpenseRecord(vehicle_info=vehicle_info)
    
    def get_vehicle(self, vehicle_name: str) -> Optional[ExpenseRecord]:
        """
        車両の実績レコードを取得
        
        Args:
            vehicle_name: 車両名
            
        Returns:
            ExpenseRecord または None
        """
        return self.records.get(vehicle_name)
    
    def list_vehicles(self) -> list[str]:
        """
        登録済み車両の一覧を取得
        
        Returns:
            車両名のリスト
        """
        return list(self.records.keys())
    
    def add_fuel_expense(self, vehicle_name: str, expense: FuelExpense) -> None:
        """ガソリン代を追加"""
        record = self.records.get(vehicle_name)
        if record is None:
            raise ValueError(f"車両 '{vehicle_name}' が見つかりません")
        record.fuel_expenses.append(expense)
    
    def add_inspection_expense(self, vehicle_name: str, expense: InspectionExpense) -> None:
        """車検費用を追加"""
        record = self.records.get(vehicle_name)
        if record is None:
            raise ValueError(f"車両 '{vehicle_name}' が見つかりません")
        record.inspection_expenses.append(expense)
    
    def add_insurance_expense(self, vehicle_name: str, expense: InsuranceExpense) -> None:
        """保険料を追加"""
        record = self.records.get(vehicle_name)
        if record is None:
            raise ValueError(f"車両 '{vehicle_name}' が見つかりません")
        record.insurance_expenses.append(expense)
    
    def add_tax_expense(self, vehicle_name: str, expense: TaxExpense) -> None:
        """自動車税を追加"""
        record = self.records.get(vehicle_name)
        if record is None:
            raise ValueError(f"車両 '{vehicle_name}' が見つかりません")
        record.tax_expenses.append(expense)
    
    def add_parking_expense(self, vehicle_name: str, expense: ParkingExpense) -> None:
        """駐車場代を追加"""
        record = self.records.get(vehicle_name)
        if record is None:
            raise ValueError(f"車両 '{vehicle_name}' が見つかりません")
        record.parking_expenses.append(expense)
    
    def add_maintenance_expense(self, vehicle_name: str, expense: MaintenanceExpense) -> None:
        """メンテナンス費用を追加"""
        record = self.records.get(vehicle_name)
        if record is None:
            raise ValueError(f"車両 '{vehicle_name}' が見つかりません")
        record.maintenance_expenses.append(expense)
    
    def save(self, filename: str = "expense_data.pkl") -> None:
        """
        データを保存
        
        Args:
            filename: 保存ファイル名
        """
        filepath = self.data_dir / filename
        with open(filepath, "wb") as f:
            pickle.dump(self.records, f)
    
    def load(self, filename: str = "expense_data.pkl") -> bool:
        """
        データを読み込み
        
        Args:
            filename: 読み込みファイル名
            
        Returns:
            読み込み成功時True、失敗時False
        """
        filepath = self.data_dir / filename
        if not filepath.exists():
            return False
        
        try:
            with open(filepath, "rb") as f:
                self.records = pickle.load(f)
            return True
        except Exception:
            return False
    
    def export_to_dict(self, vehicle_name: str) -> Optional[dict]:
        """
        車両の実績データを辞書形式でエクスポート
        
        Args:
            vehicle_name: 車両名
            
        Returns:
            辞書形式のデータ または None
        """
        record = self.records.get(vehicle_name)
        if record is None:
            return None
        
        def date_to_str(d: date) -> str:
            return d.isoformat() if d else ""
        
        return {
            "vehicle_info": {
                "name": record.vehicle_info.name,
                "purchase_date": date_to_str(record.vehicle_info.purchase_date),
                "purchase_price": record.vehicle_info.purchase_price,
                "vehicle_type": record.vehicle_info.vehicle_type,
                "fuel_type": record.vehicle_info.fuel_type,
                "displacement": record.vehicle_info.displacement,
            },
            "fuel_expenses": [
                {
                    "date": date_to_str(e.date),
                    "amount": e.amount,
                    "price_per_liter": e.price_per_liter,
                    "odometer": e.odometer,
                    "total_cost": e.total_cost,
                }
                for e in record.fuel_expenses
            ],
            "inspection_expenses": [
                {
                    "date": date_to_str(e.date),
                    "inspection_fee": e.inspection_fee,
                    "weight_tax": e.weight_tax,
                    "liability_insurance": e.liability_insurance,
                    "stamp_fee": e.stamp_fee,
                    "other_fee": e.other_fee,
                    "total_cost": e.total_cost,
                }
                for e in record.inspection_expenses
            ],
            "insurance_expenses": [
                {
                    "date": date_to_str(e.date),
                    "insurance_type": e.insurance_type,
                    "premium": e.premium,
                    "coverage_start": date_to_str(e.coverage_start) if e.coverage_start else "",
                    "coverage_end": date_to_str(e.coverage_end) if e.coverage_end else "",
                }
                for e in record.insurance_expenses
            ],
            "tax_expenses": [
                {
                    "date": date_to_str(e.date),
                    "tax_amount": e.tax_amount,
                    "tax_type": e.tax_type,
                }
                for e in record.tax_expenses
            ],
            "parking_expenses": [
                {
                    "date": date_to_str(e.date),
                    "monthly_fee": e.monthly_fee,
                    "payment_type": e.payment_type,
                }
                for e in record.parking_expenses
            ],
            "maintenance_expenses": [
                {
                    "date": date_to_str(e.date),
                    "category": e.category,
                    "cost": e.cost,
                    "description": e.description,
                    "odometer": e.odometer,
                }
                for e in record.maintenance_expenses
            ],
        }
