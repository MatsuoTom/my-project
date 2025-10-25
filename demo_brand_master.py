"""
銘柄マスタ管理機能のデモスクリプト

銘柄・投資方法・証券会社の初期登録と操作例を実行します。
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from investment_simulation.core.brand_master import BrandMaster
import pandas as pd


def print_section(title: str):
    """セクションタイトルを表示"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demo_basic_operations():
    """基本操作のデモ"""
    print_section("1️⃣  基本操作デモ")
    
    # 一時ディレクトリでBrandMasterインスタンスを作成
    import tempfile
    temp_dir = Path(tempfile.mkdtemp())
    master = BrandMaster(data_dir=temp_dir)
    
    print(f"\n✅ BrandMasterインスタンスを作成しました")
    print(f"📁 データディレクトリ: {temp_dir}")
    
    # デフォルトデータの確認
    print(f"\n📊 デフォルトデータ:")
    print(f"  - 銘柄: {len(master.brands)}件")
    print(f"  - 投資方法: {len(master.methods)}件")
    print(f"  - 証券会社: {len(master.brokers)}件")
    
    return master


def demo_brand_management(master: BrandMaster):
    """銘柄管理のデモ"""
    print_section("2️⃣  銘柄管理デモ")
    
    # 銘柄の追加
    print("\n➕ 新規銘柄を追加:")
    brands_to_add = [
        ("AAPL", "Apple Inc.", "個別株", "米国"),
        ("GOOGL", "Alphabet Inc.", "個別株", "米国"),
        ("TSLA", "Tesla Inc.", "個別株", "米国"),
        ("7203", "トヨタ自動車", "個別株", "日本"),
    ]
    
    for code, name, category, region in brands_to_add:
        result = master.add_brand(code, name, category, region)
        status = "✅" if result else "❌"
        print(f"  {status} {code}: {name} ({category}, {region})")
    
    # 銘柄の検索
    print("\n🔍 銘柄を検索:")
    apple = master.find_brand_by_code("AAPL")
    if apple:
        print(f"  銘柄コード: {apple['code']}")
        print(f"  銘柄名: {apple['name']}")
        print(f"  カテゴリ: {apple['category']}")
        print(f"  地域: {apple['region']}")
    
    # カテゴリでフィルタ
    print("\n🏷️  カテゴリ別銘柄リスト:")
    categories = master.get_categories()
    for category in categories[:3]:  # 最初の3つ
        brands = master.get_brands(category=category)
        print(f"  {category}: {len(brands)}件")
        for brand in brands[:2]:  # 各カテゴリ最初の2件
            print(f"    - {brand['code']}: {brand['name']}")
    
    # 銘柄の更新
    print("\n✏️  銘柄情報を更新:")
    master.update_brand("AAPL", name="Apple Corporation")
    updated = master.find_brand_by_code("AAPL")
    print(f"  更新後: {updated['code']} - {updated['name']}")
    
    # 表示用リスト
    print("\n📋 表示用銘柄リスト（最初の5件）:")
    display_list = master.get_brand_display_list()
    for item in display_list[:5]:
        print(f"  - {item}")


def demo_method_and_broker(master: BrandMaster):
    """投資方法・証券会社管理のデモ"""
    print_section("3️⃣  投資方法・証券会社管理デモ")
    
    # 投資方法の追加
    print("\n📈 投資方法を追加:")
    methods_to_add = ["ボーナス購入", "リバランス", "ドルコスト平均法"]
    for method in methods_to_add:
        result = master.add_method(method)
        status = "✅" if result else "❌"
        print(f"  {status} {method}")
    
    print(f"\n現在の投資方法（全{len(master.methods)}件）:")
    for method in master.get_methods():
        print(f"  - {method}")
    
    # 証券会社の追加
    print("\n🏦 証券会社を追加:")
    brokers_to_add = ["野村證券", "大和証券"]
    for broker in brokers_to_add:
        result = master.add_broker(broker)
        status = "✅" if result else "❌"
        print(f"  {status} {broker}")
    
    print(f"\n現在の証券会社（全{len(master.brokers)}件）:")
    for broker in master.get_brokers():
        print(f"  - {broker}")


def demo_bulk_import(master: BrandMaster):
    """一括インポートのデモ"""
    print_section("4️⃣  一括インポートデモ")
    
    # サンプルデータ作成
    df = pd.DataFrame({
        '銘柄': ['MSFT', 'AMZN,NVDA', 'NFLX'],
        '投資方法': ['積立', '積立', '新規購入'],
        '証券会社': ['マネックス証券', 'SBI証券', '楽天証券'],
        '投資額': [30000, 50000, 20000],
        '評価額': [32000, 52000, 19000]
    })
    
    print("\n📥 サンプルデータ:")
    print(df.to_string(index=False))
    
    print("\n⚙️  一括インポート実行中...")
    result = master.import_from_dataframe(df)
    
    print(f"\n✅ インポート完了:")
    print(f"  - 銘柄: {result['brands']}件追加")
    print(f"  - 投資方法: {result['methods']}件追加")
    print(f"  - 証券会社: {result['brokers']}件追加")
    
    # インポート後の確認
    print(f"\n現在のマスタ状況:")
    print(f"  - 銘柄: {len(master.brands)}件")
    print(f"  - 投資方法: {len(master.methods)}件")
    print(f"  - 証券会社: {len(master.brokers)}件")


def demo_persistence(master: BrandMaster):
    """永続化のデモ"""
    print_section("5️⃣  永続化デモ")
    
    master_file = master.master_file
    print(f"\n💾 マスタファイル: {master_file}")
    
    if master_file.exists():
        import json
        with open(master_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n📄 ファイル内容:")
        print(f"  - brands: {len(data.get('brands', []))}件")
        print(f"  - methods: {len(data.get('methods', []))}件")
        print(f"  - brokers: {len(data.get('brokers', []))}件")
        print(f"  - 最終更新: {data.get('last_updated', 'N/A')}")
        
        print(f"\n✅ データは自動的にJSONファイルに保存されています")
    else:
        print(f"\n❌ マスタファイルが見つかりません")


def demo_filter_and_search(master: BrandMaster):
    """フィルタ・検索のデモ"""
    print_section("6️⃣  フィルタ・検索デモ")
    
    # 地域でフィルタ
    print("\n🌍 地域別銘柄数:")
    regions = master.get_regions()
    for region in regions:
        brands = master.get_brands(region=region)
        print(f"  {region}: {len(brands)}件")
    
    # 複合フィルタ
    print("\n🔍 複合フィルタ（米国 × ETF）:")
    us_etfs = master.get_brands(category="ETF", region="米国")
    print(f"  該当: {len(us_etfs)}件")
    for brand in us_etfs:
        print(f"  - {brand['code']}: {brand['name']}")
    
    # 削除のデモ
    print("\n🗑️  銘柄削除デモ:")
    if master.find_brand_by_code("TSLA"):
        result = master.delete_brand("TSLA")
        status = "✅" if result else "❌"
        print(f"  {status} TSLAを削除しました")
        print(f"  現在の銘柄数: {len(master.brands)}件")


def main():
    """メイン関数"""
    print("\n" + "🎯" * 30)
    print("   NISA投資シミュレーション — 銘柄マスタ管理デモ")
    print("🎯" * 30)
    
    try:
        # 1. 基本操作
        master = demo_basic_operations()
        
        # 2. 銘柄管理
        demo_brand_management(master)
        
        # 3. 投資方法・証券会社管理
        demo_method_and_broker(master)
        
        # 4. 一括インポート
        demo_bulk_import(master)
        
        # 5. 永続化
        demo_persistence(master)
        
        # 6. フィルタ・検索
        demo_filter_and_search(master)
        
        print_section("✨ デモ完了")
        print("\n🎉 すべての操作が正常に完了しました！")
        print("\n📝 次のステップ:")
        print("  1. アプリを起動: python scripts/run_investment_app.py")
        print("  2. ブラウザで http://localhost:8512 にアクセス")
        print("  3. 🔧 マスタ管理タブで銘柄を登録・管理")
        print("  4. 📝 銘柄登録・データ管理タブでマスタから選択して入力")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
