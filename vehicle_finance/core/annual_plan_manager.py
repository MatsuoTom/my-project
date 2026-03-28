"""
年間維持費計画の管理

計画の作成・保存・読み込み機能
"""

import pickle
import csv
from pathlib import Path
from typing import Optional
from datetime import date

from vehicle_finance.data.annual_plan_models import (
    VehicleInfo,
    AnnualMaintenancePlan,
    VehicleMaintenancePlan,
)


class AnnualPlanManager:
    """年間維持費計画マネージャー"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        初期化
        
        Args:
            data_dir: データ保存ディレクトリ
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data" / "saved_plans"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # CSV保存用ディレクトリ
        self.csv_dir = self.data_dir / "csv"
        self.csv_dir.mkdir(parents=True, exist_ok=True)
        
        self.plans: dict[str, VehicleMaintenancePlan] = {}  # 車両名 -> 計画
    
    def add_vehicle_plan(self, vehicle_info: VehicleInfo) -> None:
        """
        車両の維持費計画を追加
        
        Args:
            vehicle_info: 車両情報
        """
        if vehicle_info.name in self.plans:
            raise ValueError(f"車両 '{vehicle_info.name}' は既に登録されています")
        
        self.plans[vehicle_info.name] = VehicleMaintenancePlan(vehicle_info=vehicle_info)
    
    def get_vehicle_plan(self, vehicle_name: str) -> Optional[VehicleMaintenancePlan]:
        """
        車両の維持費計画を取得
        
        Args:
            vehicle_name: 車両名
            
        Returns:
            VehicleMaintenancePlan または None
        """
        return self.plans.get(vehicle_name)
    
    def list_vehicles(self) -> list[str]:
        """
        登録済み車両の一覧
        
        Returns:
            車両名のリスト
        """
        return list(self.plans.keys())
    
    def create_default_plan(self, vehicle_name: str, start_year: int, num_years: int = 10) -> None:
        """
        デフォルトの年間計画を作成
        
        Args:
            vehicle_name: 車両名
            start_year: 開始年度
            num_years: 計画年数
        """
        plan_obj = self.plans.get(vehicle_name)
        if plan_obj is None:
            raise ValueError(f"車両 '{vehicle_name}' が見つかりません")
        
        vehicle = plan_obj.vehicle_info
        
        # 車検年の判定（初回3年、以降2年ごと）
        ownership_start_year = vehicle.ownership_start_year
        
        for i in range(num_years):
            year = start_year + i
            years_since_purchase = year - ownership_start_year
            
            # 車検年かどうか
            is_inspection = (years_since_purchase == 2) or (years_since_purchase > 2 and (years_since_purchase - 2) % 2 == 0)
            
            # デフォルト値（車両区分で自動車税を調整）
            if vehicle.vehicle_type == "軽自動車":
                tax_amount = 10800.0
                weight_tax = 6600.0
            elif vehicle.vehicle_type == "小型車":
                tax_amount = 29500.0
                weight_tax = 24600.0
            elif vehicle.vehicle_type == "普通車":
                if vehicle.displacement and vehicle.displacement <= 1500:
                    tax_amount = 30500.0
                elif vehicle.displacement and vehicle.displacement <= 2000:
                    tax_amount = 36000.0
                elif vehicle.displacement and vehicle.displacement <= 2500:
                    tax_amount = 43500.0
                else:
                    tax_amount = 50000.0
                weight_tax = 32800.0
            else:
                tax_amount = 39500.0
                weight_tax = 32800.0
            
            annual_plan = AnnualMaintenancePlan(
                year=year,
                inspection_year=is_inspection,
                automobile_tax=tax_amount,
                weight_tax=weight_tax,
            )
            
            plan_obj.add_year_plan(annual_plan)
    
    def save(self, filename: str = "annual_plans.pkl") -> None:
        """
        計画を保存（Pickle + 自動CSV出力）
        
        Args:
            filename: 保存ファイル名
        """
        # Pickle保存
        filepath = self.data_dir / filename
        with open(filepath, "wb") as f:
            pickle.dump(self.plans, f)
        
        # 各車両のCSVを自動保存
        self._save_all_csv()
    
    def _save_all_csv(self) -> None:
        """すべての車両の計画と実績をCSV保存"""
        for vehicle_name, plan_obj in self.plans.items():
            # 安全なファイル名に変換
            safe_name = vehicle_name.replace("/", "_").replace("\\", "_")
            
            # 計画CSVを保存
            self._save_plan_csv(safe_name, plan_obj)
            
            # 実績CSVを保存
            self._save_actual_csv(safe_name, plan_obj)
    
    def _save_plan_csv(self, vehicle_name: str, plan_obj: VehicleMaintenancePlan) -> None:
        """計画データをCSV保存"""
        if not plan_obj.annual_plans:
            return
        
        csv_path = self.csv_dir / f"{vehicle_name}_計画.csv"
        
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # ヘッダー
            writer.writerow([
                '年度', '車検年', '年間走行距離', '燃費', '燃料単価', '燃料費',
                '車検基本料', '重量税', '自賠責保険', '車検その他', '車検費用合計',
                '任意保険', '自動車税', '月額駐車場代', '駐車場代年額',
                'オイル交換回数', 'オイル交換単価', 'タイヤ交換', 'タイヤ交換費用',
                'その他メンテ', '洗車消耗品', '予備費', '年間合計'
            ])
            
            # データ行
            for plan in sorted(plan_obj.annual_plans, key=lambda p: p.year):
                writer.writerow([
                    plan.year,
                    '○' if plan.inspection_year else '',
                    plan.annual_mileage,
                    plan.fuel_efficiency,
                    plan.fuel_price_per_liter,
                    f'{plan.fuel_cost:.0f}',
                    f'{plan.inspection_base_fee:.0f}',
                    f'{plan.weight_tax:.0f}',
                    f'{plan.liability_insurance:.0f}',
                    f'{plan.inspection_other:.0f}',
                    f'{plan.inspection_cost:.0f}',
                    f'{plan.voluntary_insurance:.0f}',
                    f'{plan.automobile_tax:.0f}',
                    f'{plan.monthly_parking_fee:.0f}',
                    f'{plan.parking_cost:.0f}',
                    plan.oil_change_count,
                    f'{plan.oil_change_cost:.0f}',
                    '○' if plan.tire_change else '',
                    f'{plan.tire_change_cost:.0f}',
                    f'{plan.other_maintenance:.0f}',
                    f'{plan.car_wash:.0f}',
                    f'{plan.unexpected_expense:.0f}',
                    f'{plan.total_annual_cost:.0f}'
                ])
    
    def _save_actual_csv(self, vehicle_name: str, plan_obj: VehicleMaintenancePlan) -> None:
        """実績データをCSV保存"""
        if not plan_obj.actual_expenses:
            return
        
        csv_path = self.csv_dir / f"{vehicle_name}_実績.csv"
        
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # ヘッダー
            writer.writerow([
                '年度', '燃料費', '車検', '保険', '税金',
                'オイル交換', 'タイヤ交換', 'その他メンテ', 'メンテ合計',
                'その他', '合計', '計画額', '計画比'
            ])
            
            # データ行
            for actual in sorted(plan_obj.actual_expenses, key=lambda a: a.year):
                plan = plan_obj.get_year_plan(actual.year)
                plan_total = plan.total_annual_cost if plan else 0
                diff = actual.total_cost - plan_total
                
                writer.writerow([
                    actual.year,
                    f'{actual.fuel_cost:.0f}',
                    f'{actual.inspection_cost:.0f}',
                    f'{actual.insurance_cost:.0f}',
                    f'{actual.tax_cost:.0f}',
                    f'{actual.oil_change_cost:.0f}',
                    f'{actual.tire_change_cost:.0f}',
                    f'{actual.other_maintenance_cost:.0f}',
                    f'{actual.total_maintenance_cost:.0f}',
                    f'{actual.other_cost:.0f}',
                    f'{actual.total_cost:.0f}',
                    f'{plan_total:.0f}' if plan else '',
                    f'{diff:+.0f}' if plan else ''
                ])
    
    def load(self, filename: str = "annual_plans.pkl") -> bool:
        """
        計画を読み込み
        
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
                self.plans = pickle.load(f)
            return True
        except Exception:
            return False
