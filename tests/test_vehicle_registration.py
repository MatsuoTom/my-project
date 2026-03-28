"""
車両登録のテストスクリプト
"""

from datetime import date
from vehicle_finance.core.annual_plan_manager import AnnualPlanManager
from vehicle_finance.data.annual_plan_models import VehicleInfo

# マネージャーを作成
manager = AnnualPlanManager()

# 車両情報を作成
vehicle_info = VehicleInfo(
    name="テスト車両",
    ownership_start_year=2024,
    purchase_price=2000000.0,
    vehicle_type="普通車",
    fuel_type="ガソリン",
    displacement=1500,
)

print(f"車両情報: {vehicle_info}")

try:
    # 車両を追加
    manager.add_vehicle_plan(vehicle_info)
    print("✅ 車両追加成功")
    
    # デフォルト計画を作成
    manager.create_default_plan("テスト車両", 2024, num_years=10)
    print("✅ 計画作成成功")
    
    # 計画を取得
    plan_obj = manager.get_vehicle_plan("テスト車両")
    print(f"✅ 計画取得成功: {len(plan_obj.annual_plans)}年分")
    
    # 2024年の計画を表示
    plan_2024 = plan_obj.get_year_plan(2024)
    if plan_2024:
        print(f"2024年の維持費: {plan_2024.total_annual_cost:,.0f}円")
        print(f"車検年: {plan_2024.inspection_year}")
    
    # 保存
    manager.save()
    print("✅ 保存成功")
    
except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()
