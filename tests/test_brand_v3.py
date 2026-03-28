"""銘柄マスタv3の動作確認スクリプト"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from investment_simulation.core.brand_master import BrandMaster
from datetime import datetime

# テスト用一時ディレクトリ
import tempfile
temp_dir = Path(tempfile.mkdtemp())
print(f"テスト用ディレクトリ: {temp_dir}")

# BrandMasterインスタンス作成
master = BrandMaster(data_dir=temp_dir)
print(f"\n✅ 初期化成功: {len(master.brands)}件の銘柄が読み込まれました")

# テスト1: 新規銘柄追加（現在価格・利益額入力）
print("\n--- テスト1: 新規銘柄追加 ---")
result = master.add_brand(
    code="TEST001",
    name="テスト銘柄1",
    broker="SBI証券",
    account="積立NISA",
    category="ETF",
    region="米国",
    current_price=1200000.0,  # 現在価格: 120万円
    profit=200000.0,          # 利益額: 20万円
    investment_date="2020-01-01"  # 投資開始日: 2020年1月1日
)

if result:
    print("✅ 銘柄追加成功")
    brand = master.find_brand_by_code("TEST001")
    print(f"  コード: {brand['code']}")
    print(f"  銘柄名: {brand['name']}")
    print(f"  現在価格: ¥{brand['current_price']:,.0f}")
    print(f"  利益額: ¥{brand['profit']:,.0f}")
    print(f"  投資開始日: {brand['investment_date']}")
    print(f"  元本（自動計算）: ¥{brand['principal']:,.0f}")
    print(f"  利率（自動計算）: {brand['profit_rate']:.2f}%")
    print(f"  年利（自動計算）: {brand['annual_return']:.2f}%")
else:
    print("❌ 銘柄追加失敗")

# テスト2: 銘柄更新
print("\n--- テスト2: 銘柄更新 ---")
result = master.update_brand(
    code="TEST001",
    current_price=1500000.0,  # 現在価格を150万円に更新
    profit=300000.0           # 利益額を30万円に更新
)

if result:
    print("✅ 銘柄更新成功")
    brand = master.find_brand_by_code("TEST001")
    print(f"  更新後の現在価格: ¥{brand['current_price']:,.0f}")
    print(f"  更新後の利益額: ¥{brand['profit']:,.0f}")
    print(f"  更新後の元本: ¥{brand['principal']:,.0f}")
    print(f"  更新後の利率: {brand['profit_rate']:.2f}%")
    print(f"  更新後の年利: {brand['annual_return']:.2f}%")
else:
    print("❌ 銘柄更新失敗")

# テスト3: 年利計算の検証
print("\n--- テスト3: 年利計算の検証 ---")
# 元本100万円、5年後に120万円（利益20万円）の場合
# 年利 = (1.2)^(1/5) - 1 ≈ 3.71%
result = master.add_brand(
    code="TEST002",
    name="年利計算テスト",
    broker="楽天証券",
    account="特定",
    category="投資信託",
    region="全世界",
    current_price=1200000.0,
    profit=200000.0,
    investment_date=(datetime.now().replace(year=datetime.now().year-5)).strftime('%Y-%m-%d')
)

if result:
    brand = master.find_brand_by_code("TEST002")
    print(f"  元本: ¥{brand['principal']:,.0f}")
    print(f"  5年後の評価額: ¥{brand['current_price']:,.0f}")
    print(f"  利益: ¥{brand['profit']:,.0f}")
    print(f"  利率: {brand['profit_rate']:.2f}%")
    print(f"  年利: {brand['annual_return']:.2f}% (期待値: 約3.71%)")
else:
    print("❌ テスト失敗")

# テスト4: 全銘柄取得
print("\n--- テスト4: 全銘柄取得 ---")
all_brands = master.get_brands()
print(f"登録銘柄数: {len(all_brands)}件")

# クリーンアップ
import shutil
shutil.rmtree(temp_dir)
print(f"\n✅ テスト完了。一時ディレクトリを削除しました。")
