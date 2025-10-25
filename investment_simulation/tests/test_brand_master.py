"""
銘柄マスタ管理モジュールのテスト

BrandMasterクラスの機能をテストします。
"""

import pytest
import pandas as pd
from pathlib import Path
import json
import tempfile
import shutil

from investment_simulation.core.brand_master import BrandMaster


@pytest.fixture
def temp_data_dir():
    """テスト用一時ディレクトリ"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # テスト後にクリーンアップ
    shutil.rmtree(temp_dir)


@pytest.fixture
def brand_master(temp_data_dir):
    """テスト用BrandMasterインスタンス"""
    return BrandMaster(data_dir=temp_data_dir)


class TestBrandMasterInitialization:
    """初期化のテスト"""
    
    def test_initialization_creates_default_data(self, brand_master):
        """初期化時にデフォルトデータが作成される"""
        assert len(brand_master.brands) > 0
        assert len(brand_master.methods) > 0
        assert len(brand_master.brokers) > 0
    
    def test_initialization_creates_json_file(self, temp_data_dir):
        """初期化時にJSONファイルが作成される"""
        master = BrandMaster(data_dir=temp_data_dir)
        master_file = temp_data_dir / "brand_master.json"
        assert master_file.exists()
    
    def test_load_existing_master_data(self, temp_data_dir):
        """既存のマスタデータを読み込める"""
        # 最初のインスタンスでデータ作成
        master1 = BrandMaster(data_dir=temp_data_dir)
        master1.add_brand("TEST", "テスト銘柄", "ETF", "米国")
        
        # 新しいインスタンスで読み込み
        master2 = BrandMaster(data_dir=temp_data_dir)
        assert any(b['code'] == "TEST" for b in master2.brands)


class TestBrandManagement:
    """銘柄管理機能のテスト"""
    
    def test_add_brand_success(self, brand_master):
        """銘柄の追加が成功する"""
        result = brand_master.add_brand("AAPL", "Apple Inc.", "SBI証券", "特定", "個別株", "米国", 100000.0, 80000.0)
        assert result is True
        assert any(b['code'] == "AAPL" for b in brand_master.brands)
        brand = brand_master.find_brand_by_code("AAPL")
        assert brand['current_price'] == 100000.0
        assert brand['principal'] == 80000.0
    
    def test_add_brand_duplicate(self, brand_master):
        """重複する銘柄コードは追加できない"""
        brand_master.add_brand("AAPL", "Apple Inc.", "SBI証券", "特定", "個別株", "米国", 100000.0, 80000.0)
        result = brand_master.add_brand("AAPL", "Apple Inc. 2", "楽天証券", "NISA", "個別株", "米国", 50000.0, 50000.0)
        assert result is False
    
    def test_update_brand_success(self, brand_master):
        """銘柄情報の更新が成功する"""
        brand_master.add_brand("AAPL", "Apple Inc.", "SBI証券", "特定", "個別株", "米国", 100000.0, 80000.0)
        result = brand_master.update_brand("AAPL", name="Apple Corp.", category="ETF", account="NISA", 
                                          current_price=120000.0, principal=85000.0)
        assert result is True
        
        brand = brand_master.find_brand_by_code("AAPL")
        assert brand['name'] == "Apple Corp."
        assert brand['category'] == "ETF"
        assert brand['account'] == "NISA"
        assert brand['current_price'] == 120000.0
        assert brand['principal'] == 85000.0
    
    def test_update_brand_not_found(self, brand_master):
        """存在しない銘柄の更新は失敗する"""
        result = brand_master.update_brand("NOTEXIST", name="Test")
        assert result is False
    
    def test_delete_brand_success(self, brand_master):
        """銘柄の削除が成功する"""
        brand_master.add_brand("AAPL", "Apple Inc.", "SBI証券", "特定", "個別株", "米国", 100000.0, 80000.0)
        original_count = len(brand_master.brands)
        
        result = brand_master.delete_brand("AAPL")
        assert result is True
        assert len(brand_master.brands) == original_count - 1
        assert not any(b['code'] == "AAPL" for b in brand_master.brands)
    
    def test_delete_brand_not_found(self, brand_master):
        """存在しない銘柄の削除は失敗する"""
        result = brand_master.delete_brand("NOTEXIST")
        assert result is False
    
    def test_get_brands_no_filter(self, brand_master):
        """フィルタなしで全銘柄を取得"""
        brands = brand_master.get_brands()
        assert len(brands) == len(brand_master.brands)
    
    def test_get_brands_with_category_filter(self, brand_master):
        """カテゴリでフィルタして銘柄を取得"""
        brand_master.add_brand("TEST1", "Test 1", "", "特定", "ETF", "米国", 50000.0, 50000.0)
        brand_master.add_brand("TEST2", "Test 2", "", "NISA", "投資信託", "米国", 30000.0, 30000.0)
        
        etf_brands = brand_master.get_brands(category="ETF")
        assert all(b['category'] == "ETF" for b in etf_brands)
    
    def test_get_brands_with_region_filter(self, brand_master):
        """地域でフィルタして銘柄を取得"""
        brand_master.add_brand("TEST1", "Test 1", "SBI証券", "特定", "ETF", "米国", 50000.0, 50000.0)
        brand_master.add_brand("TEST2", "Test 2", "楽天証券", "NISA", "ETF", "日本", 30000.0, 30000.0)
        
        us_brands = brand_master.get_brands(region="米国")
        assert all(b['region'] == "米国" for b in us_brands)
    
    def test_find_brand_by_code_success(self, brand_master):
        """銘柄コードで検索が成功する"""
        brand_master.add_brand("AAPL", "Apple Inc.", "SBI証券", "特定", "個別株", "米国", 100000.0, 80000.0)
        brand = brand_master.find_brand_by_code("AAPL")
        assert brand is not None
        assert brand['code'] == "AAPL"
        assert brand['name'] == "Apple Inc."
    
    def test_find_brand_by_code_not_found(self, brand_master):
        """存在しない銘柄コードはNoneを返す"""
        brand = brand_master.find_brand_by_code("NOTEXIST")
        assert brand is None
    
    def test_get_brand_display_list(self, brand_master):
        """表示用銘柄リストを取得"""
        brand_master.add_brand("AAPL", "Apple Inc.", "SBI証券", "特定", "個別株", "米国", 100000.0, 80000.0)
        display_list = brand_master.get_brand_display_list()
        assert any("AAPL: Apple Inc." in item for item in display_list)
    
    def test_get_brand_code_list(self, brand_master):
        """銘柄コードリストを取得"""
        brand_master.add_brand("AAPL", "Apple Inc.", "SBI証券", "特定", "個別株", "米国", 100000.0, 80000.0)
        code_list = brand_master.get_brand_code_list()
        assert "AAPL" in code_list


class TestMethodManagement:
    """投資方法管理機能のテスト"""
    
    def test_add_method_success(self, brand_master):
        """投資方法の追加が成功する"""
        result = brand_master.add_method("テスト投資方法")
        assert result is True
        assert "テスト投資方法" in brand_master.methods
    
    def test_add_method_duplicate(self, brand_master):
        """重複する投資方法は追加できない"""
        brand_master.add_method("テスト投資方法")
        result = brand_master.add_method("テスト投資方法")
        assert result is False
    
    def test_delete_method_success(self, brand_master):
        """投資方法の削除が成功する"""
        brand_master.add_method("テスト投資方法")
        result = brand_master.delete_method("テスト投資方法")
        assert result is True
        assert "テスト投資方法" not in brand_master.methods
    
    def test_delete_method_not_found(self, brand_master):
        """存在しない投資方法の削除は失敗する"""
        result = brand_master.delete_method("存在しない投資方法")
        assert result is False
    
    def test_get_methods(self, brand_master):
        """投資方法リストを取得"""
        methods = brand_master.get_methods()
        assert isinstance(methods, list)
        assert len(methods) > 0


class TestBrokerManagement:
    """証券会社管理機能のテスト"""
    
    def test_add_broker_success(self, brand_master):
        """証券会社の追加が成功する"""
        result = brand_master.add_broker("テスト証券")
        assert result is True
        assert "テスト証券" in brand_master.brokers
    
    def test_add_broker_duplicate(self, brand_master):
        """重複する証券会社は追加できない"""
        brand_master.add_broker("テスト証券")
        result = brand_master.add_broker("テスト証券")
        assert result is False
    
    def test_delete_broker_success(self, brand_master):
        """証券会社の削除が成功する"""
        brand_master.add_broker("テスト証券")
        result = brand_master.delete_broker("テスト証券")
        assert result is True
        assert "テスト証券" not in brand_master.brokers
    
    def test_delete_broker_not_found(self, brand_master):
        """存在しない証券会社の削除は失敗する"""
        result = brand_master.delete_broker("存在しない証券")
        assert result is False
    
    def test_get_brokers(self, brand_master):
        """証券会社リストを取得"""
        brokers = brand_master.get_brokers()
        assert isinstance(brokers, list)
        assert len(brokers) > 0


class TestCategoryAndRegion:
    """カテゴリ・地域・口座取得のテスト"""
    
    def test_get_categories(self, brand_master):
        """カテゴリリストを取得"""
        categories = brand_master.get_categories()
        assert isinstance(categories, list)
        assert "ETF" in categories or "投資信託" in categories
    
    def test_get_regions(self, brand_master):
        """地域リストを取得"""
        regions = brand_master.get_regions()
        assert isinstance(regions, list)
        assert "米国" in regions or "全世界" in regions
    
    def test_get_accounts(self, brand_master):
        """口座種別リストを取得"""
        accounts = brand_master.get_accounts()
        assert isinstance(accounts, list)
        assert "積立NISA" in accounts or "NISA" in accounts or "特定" in accounts


class TestBulkOperations:
    """一括操作のテスト"""
    
    def test_import_from_dataframe(self, brand_master):
        """DataFrameから一括インポート"""
        df = pd.DataFrame({
            '銘柄': ['AAPL', 'GOOGL', 'MSFT'],
            '投資方法': ['積立', 'カスタム投資1', 'カスタム投資2'],
            '証券会社': ['カスタム証券1', 'カスタム証券2', 'カスタム証券1']
        })
        
        result = brand_master.import_from_dataframe(df)
        
        assert result['brands'] == 3
        assert result['methods'] >= 2  # カスタム投資1, カスタム投資2（積立はデフォルトに含まれる）
        assert result['brokers'] == 2  # カスタム証券1, カスタム証券2
        
        # 銘柄が追加されたか確認
        assert any(b['code'] == 'AAPL' for b in brand_master.brands)
        assert any(b['code'] == 'GOOGL' for b in brand_master.brands)
        assert any(b['code'] == 'MSFT' for b in brand_master.brands)
        
        # 投資方法・証券会社が追加されたか確認
        assert 'カスタム投資1' in brand_master.methods
        assert 'カスタム投資2' in brand_master.methods
        assert 'カスタム証券1' in brand_master.brokers
        assert 'カスタム証券2' in brand_master.brokers
    
    def test_import_from_dataframe_with_comma_separated_brands(self, brand_master):
        """カンマ区切り銘柄のDataFrameから一括インポート"""
        df = pd.DataFrame({
            '銘柄': ['AAPL,GOOGL', 'MSFT'],
            '投資方法': ['積立', '積立'],
            '証券会社': ['SBI証券', 'SBI証券']
        })
        
        result = brand_master.import_from_dataframe(df)
        
        assert result['brands'] == 3
        assert any(b['code'] == 'AAPL' for b in brand_master.brands)
        assert any(b['code'] == 'GOOGL' for b in brand_master.brands)
        assert any(b['code'] == 'MSFT' for b in brand_master.brands)
    
    def test_reset_to_default(self, brand_master):
        """デフォルトにリセット"""
        # カスタムデータ追加
        brand_master.add_brand("CUSTOM", "Custom Brand", "ETF", "米国")
        brand_master.add_method("カスタム投資方法")
        
        # リセット
        brand_master.reset_to_default()
        
        # カスタムデータが消えていることを確認
        assert not any(b['code'] == 'CUSTOM' for b in brand_master.brands)
        assert "カスタム投資方法" not in brand_master.methods


class TestPersistence:
    """永続化のテスト"""
    
    def test_data_persists_across_instances(self, temp_data_dir):
        """データが複数インスタンス間で永続化される"""
        # 最初のインスタンスでデータ追加
        master1 = BrandMaster(data_dir=temp_data_dir)
        master1.add_brand("PERSIST", "Persist Brand", "ETF", "米国")
        master1.add_method("永続化テスト")
        master1.add_broker("永続化証券")
        
        # 新しいインスタンスで読み込み
        master2 = BrandMaster(data_dir=temp_data_dir)
        
        # データが永続化されていることを確認
        assert any(b['code'] == 'PERSIST' for b in master2.brands)
        assert "永続化テスト" in master2.methods
        assert "永続化証券" in master2.brokers
    
    def test_json_file_structure(self, temp_data_dir):
        """JSONファイルの構造が正しい"""
        master = BrandMaster(data_dir=temp_data_dir)
        master.add_brand("TEST", "Test Brand", "ETF", "米国")
        
        master_file = temp_data_dir / "brand_master.json"
        with open(master_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert 'brands' in data
        assert 'methods' in data
        assert 'brokers' in data
        assert 'last_updated' in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
