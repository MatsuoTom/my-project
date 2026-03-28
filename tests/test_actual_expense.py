"""
実績入力機能のテスト
"""

from vehicle_finance.core.annual_plan_manager import AnnualPlanManager
from vehicle_finance.data.annual_plan_models import (
    VehicleInfo,
    ActualExpense,
)

# マネージャーを作成
manager = AnnualPlanManager()

# 既存データを読み込み
loaded = manager.load()
print(f"データ読み込み: {'成功' if loaded else '新規作成'}")

# 車両がない場合は作成
if not manager.list_vehicles():
    print("\n車両を作成します...")
    vehicle_info = VehicleInfo(
        name="テスト車両",
        ownership_start_year=2024,
        purchase_price=2000000.0,
        vehicle_type="普通車",
        fuel_type="ガソリン",
        displacement=1500,
    )
    manager.add_vehicle_plan(vehicle_info)
    manager.create_default_plan("テスト車両", 2024, num_years=3)
    manager.save()
    print("✅ 車両作成完了")

# 車両を取得
vehicle_name = manager.list_vehicles()[0]
plan_obj = manager.get_vehicle_plan(vehicle_name)

print(f"\n車両名: {vehicle_name}")
print(f"計画年数: {len(plan_obj.annual_plans)}年")

# 2024年の実績を追加
print("\n2024年の実績を追加...")
actual_2024 = ActualExpense(
    year=2024,
    fuel_cost=120000.0,
    inspection_cost=0.0,
    insurance_cost=55000.0,
    tax_cost=39500.0,
    parking_cost=120000.0,
    maintenance_cost=15000.0,
    other_cost=10000.0,
)

print(f"合計実績費用: {actual_2024.total_cost:,.0f} 円")

plan_obj.add_actual_expense(actual_2024)
manager.save()

print("✅ 実績追加完了")

# 実績を取得して確認
retrieved = plan_obj.get_actual_expense(2024)
if retrieved:
    print(f"\n取得した実績:")
    print(f"  年度: {retrieved.year}")
    print(f"  燃料費: {retrieved.fuel_cost:,.0f} 円")
    print(f"  保険料: {retrieved.insurance_cost:,.0f} 円")
    print(f"  合計: {retrieved.total_cost:,.0f} 円")
else:
    print("❌ 実績取得失敗")

# 計画との比較
plan_2024 = plan_obj.get_year_plan(2024)
if plan_2024:
    diff = actual_2024.total_cost - plan_2024.total_annual_cost
    print(f"\n計画との比較:")
    print(f"  計画: {plan_2024.total_annual_cost:,.0f} 円")
    print(f"  実績: {actual_2024.total_cost:,.0f} 円")
    print(f"  差異: {diff:+,.0f} 円")
