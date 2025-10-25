"""
銘柄マスタ管理モジュール

NISA投資シミュレーションで使用する銘柄・投資方法・証券会社の
マスタデータを管理します。

機能:
- 銘柄の登録・編集・削除
- カテゴリ（ETF、投資信託、個別株等）による分類
- マスタデータの永続化（JSON）
- 入力時の選択リスト提供
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd


class BrandMaster:
    """銘柄マスタ管理クラス"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        初期化
        
        Args:
            data_dir: マスタデータ保存ディレクトリ（Noneの場合はデフォルト）
        """
        if data_dir is None:
            # デフォルトはinvestment_simulation/data/
            self.data_dir = Path(__file__).parent.parent / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.master_file = self.data_dir / "brand_master.json"
        
        # マスタデータの初期化
        self.brands: List[Dict] = []
        self.methods: List[str] = []
        self.brokers: List[str] = []
        
        self._load_master()
    
    def _load_master(self):
        """マスタデータの読み込み"""
        if self.master_file.exists():
            try:
                with open(self.master_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.brands = data.get('brands', [])
                    self.methods = data.get('methods', [])
                    self.brokers = data.get('brokers', [])
            except Exception as e:
                print(f"マスタデータ読み込みエラー: {e}")
                self._initialize_default_data()
        else:
            self._initialize_default_data()
    
    def _save_master(self) -> bool:
        """
        マスタデータの保存
        
        Returns:
            成功時True、失敗時False
        """
        try:
            data = {
                'brands': self.brands,
                'methods': self.methods,
                'brokers': self.brokers,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.master_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"マスタデータ保存エラー: {e}")
            return False
    
    def _initialize_default_data(self):
        """デフォルトマスタデータの初期化"""
        self.brands = [
            {"code": "VTI", "name": "Vanguard Total Stock Market ETF", "broker": "SBI証券", "account": "積立NISA", "category": "ETF", "region": "米国", "current_price": 0.0, "profit": 0.0, "investment_date": ""},
            {"code": "VOO", "name": "Vanguard S&P 500 ETF", "broker": "SBI証券", "account": "特定", "category": "ETF", "region": "米国", "current_price": 0.0, "profit": 0.0, "investment_date": ""},
            {"code": "VT", "name": "Vanguard Total World Stock ETF", "broker": "楽天証券", "account": "積立NISA", "category": "ETF", "region": "全世界", "current_price": 0.0, "profit": 0.0, "investment_date": ""},
            {"code": "1655", "name": "iシェアーズ S&P500米国株ETF", "broker": "SBI証券", "account": "NISA", "category": "ETF", "region": "米国", "current_price": 0.0, "profit": 0.0, "investment_date": ""},
            {"code": "2558", "name": "MAXIS米国株式(S&P500)上場投信", "broker": "楽天証券", "account": "NISA", "category": "ETF", "region": "米国", "current_price": 0.0, "profit": 0.0, "investment_date": ""},
            {"code": "emaxis-slim-sp500", "name": "eMAXIS Slim 米国株式(S&P500)", "broker": "SBI証券", "account": "積立NISA", "category": "投資信託", "region": "米国", "current_price": 0.0, "profit": 0.0, "investment_date": ""},
            {"code": "emaxis-slim-allcountry", "name": "eMAXIS Slim 全世界株式(オール・カントリー)", "broker": "楽天証券", "account": "積立NISA", "category": "投資信託", "region": "全世界", "current_price": 0.0, "profit": 0.0, "investment_date": ""},
            {"code": "楽天VTI", "name": "楽天・全米株式インデックス・ファンド", "broker": "楽天証券", "account": "積立NISA", "category": "投資信託", "region": "米国", "current_price": 0.0, "profit": 0.0, "investment_date": ""},
        ]
        
        self.methods = [
            "新規購入",
            "積立",
            "スポット購入",
            "配当再投資"
        ]
        
        self.brokers = [
            "SBI証券",
            "楽天証券",
            "マネックス証券",
            "松井証券",
            "auカブコム証券"
        ]
        
        self._save_master()
    
    # ========== 銘柄管理 ==========
    
    def get_brands(self, category: Optional[str] = None, region: Optional[str] = None) -> List[Dict]:
        """
        銘柄リストの取得
        
        Args:
            category: カテゴリでフィルタ（ETF、投資信託等）
            region: 地域でフィルタ（米国、全世界等）
        
        Returns:
            銘柄リスト
        """
        result = self.brands
        
        if category:
            result = [b for b in result if b.get('category') == category]
        
        if region:
            result = [b for b in result if b.get('region') == region]
        
        return result
    
    def add_brand(self, code: str, name: str, broker: str = "", account: str = "特定", 
                  category: str = "その他", region: str = "その他", 
                  current_price: float = 0.0, profit: float = 0.0, 
                  investment_date: str = "") -> bool:
        """
        銘柄の追加
        
        Args:
            code: 銘柄コード（ティッカーシンボル等）
            name: 銘柄名
            broker: 証券会社
            account: 口座種別（積立NISA/特定/NISA）
            category: カテゴリ
            region: 地域
            current_price: 現在価格（評価額）
            profit: 利益額
            investment_date: 投資開始日（YYYY-MM-DD形式）
        
        Returns:
            成功時True、失敗時False
        """
        # 重複チェック
        if any(b['code'] == code for b in self.brands):
            print(f"銘柄コード '{code}' は既に登録されています")
            return False
        
        # 元本、利率、年利を計算
        principal = current_price - profit
        profit_rate = (profit / principal * 100) if principal > 0 else 0.0
        annual_return = self._calculate_annual_return(profit, principal, investment_date)
        
        brand = {
            'code': code,
            'name': name,
            'broker': broker,
            'account': account,
            'category': category,
            'region': region,
            'current_price': current_price,
            'profit': profit,
            'investment_date': investment_date,
            'principal': principal,
            'profit_rate': profit_rate,
            'annual_return': annual_return,
            'created_at': datetime.now().isoformat()
        }
        
        self.brands.append(brand)
        return self._save_master()
    
    def _calculate_annual_return(self, profit: float, principal: float, investment_date: str) -> float:
        """
        年利を計算
        
        Args:
            profit: 利益額
            principal: 元本
            investment_date: 投資開始日（YYYY-MM-DD形式）
        
        Returns:
            年利（%）
        """
        if principal <= 0:
            return 0.0
        
        if not investment_date:
            return 0.0
        
        try:
            from datetime import datetime
            start_date = datetime.fromisoformat(investment_date)
            today = datetime.now()
            days = (today - start_date).days
            
            if days <= 0:
                return 0.0
            
            years = days / 365.25
            profit_rate = profit / principal
            
            # 年利 = (1 + 利益率)^(1/年数) - 1
            if profit_rate > -1:  # 元本割れでも計算可能
                annual_return = (pow(1 + profit_rate, 1 / years) - 1) * 100
            else:
                annual_return = 0.0
            
            return annual_return
        except:
            return 0.0
    
    def update_brand(self, code: str, name: Optional[str] = None, broker: Optional[str] = None,
                     account: Optional[str] = None, category: Optional[str] = None, 
                     region: Optional[str] = None, current_price: Optional[float] = None,
                     profit: Optional[float] = None, investment_date: Optional[str] = None) -> bool:
        """
        銘柄情報の更新
        
        Args:
            code: 銘柄コード
            name: 新しい銘柄名（Noneの場合は変更なし）
            broker: 新しい証券会社（Noneの場合は変更なし）
            account: 新しい口座種別（Noneの場合は変更なし）
            category: 新しいカテゴリ（Noneの場合は変更なし）
            region: 新しい地域（Noneの場合は変更なし）
            current_price: 新しい現在価格（Noneの場合は変更なし）
            profit: 新しい利益額（Noneの場合は変更なし）
            investment_date: 新しい投資開始日（Noneの場合は変更なし）
        
        Returns:
            成功時True、失敗時False
        """
        for brand in self.brands:
            if brand['code'] == code:
                if name is not None:
                    brand['name'] = name
                if broker is not None:
                    brand['broker'] = broker
                if account is not None:
                    brand['account'] = account
                if category is not None:
                    brand['category'] = category
                if region is not None:
                    brand['region'] = region
                if current_price is not None:
                    brand['current_price'] = current_price
                if profit is not None:
                    brand['profit'] = profit
                if investment_date is not None:
                    brand['investment_date'] = investment_date
                
                # 元本、利率、年利を再計算
                current = brand.get('current_price', 0.0)
                prof = brand.get('profit', 0.0)
                inv_date = brand.get('investment_date', '')
                
                principal = current - prof
                profit_rate = (prof / principal * 100) if principal > 0 else 0.0
                annual_return = self._calculate_annual_return(prof, principal, inv_date)
                
                brand['principal'] = principal
                brand['profit_rate'] = profit_rate
                brand['annual_return'] = annual_return
                brand['updated_at'] = datetime.now().isoformat()
                
                return self._save_master()
        
        print(f"銘柄コード '{code}' が見つかりません")
        return False
    
    def delete_brand(self, code: str) -> bool:
        """
        銘柄の削除
        
        Args:
            code: 銘柄コード
        
        Returns:
            成功時True、失敗時False
        """
        original_count = len(self.brands)
        self.brands = [b for b in self.brands if b['code'] != code]
        
        if len(self.brands) < original_count:
            return self._save_master()
        else:
            print(f"銘柄コード '{code}' が見つかりません")
            return False
    
    def get_brand_display_list(self) -> List[str]:
        """
        UI表示用の銘柄リスト（コード: 名前）
        
        Returns:
            表示用銘柄リスト
        """
        return [f"{b['code']}: {b['name']}" for b in self.brands]
    
    def get_brand_code_list(self) -> List[str]:
        """
        銘柄コードのみのリスト
        
        Returns:
            銘柄コードリスト
        """
        return [b['code'] for b in self.brands]
    
    def find_brand_by_code(self, code: str) -> Optional[Dict]:
        """
        銘柄コードで検索
        
        Args:
            code: 銘柄コード
        
        Returns:
            銘柄情報（見つからない場合はNone）
        """
        for brand in self.brands:
            if brand['code'] == code:
                return brand
        return None
    
    # ========== 投資方法管理 ==========
    
    def get_methods(self) -> List[str]:
        """投資方法リストの取得"""
        return self.methods
    
    def add_method(self, method: str) -> bool:
        """
        投資方法の追加
        
        Args:
            method: 投資方法名
        
        Returns:
            成功時True、失敗時False
        """
        if method in self.methods:
            print(f"投資方法 '{method}' は既に登録されています")
            return False
        
        self.methods.append(method)
        return self._save_master()
    
    def delete_method(self, method: str) -> bool:
        """
        投資方法の削除
        
        Args:
            method: 投資方法名
        
        Returns:
            成功時True、失敗時False
        """
        if method in self.methods:
            self.methods.remove(method)
            return self._save_master()
        else:
            print(f"投資方法 '{method}' が見つかりません")
            return False
    
    # ========== 証券会社管理 ==========
    
    def get_brokers(self) -> List[str]:
        """証券会社リストの取得"""
        return self.brokers
    
    def add_broker(self, broker: str) -> bool:
        """
        証券会社の追加
        
        Args:
            broker: 証券会社名
        
        Returns:
            成功時True、失敗時False
        """
        if broker in self.brokers:
            print(f"証券会社 '{broker}' は既に登録されています")
            return False
        
        self.brokers.append(broker)
        return self._save_master()
    
    def delete_broker(self, broker: str) -> bool:
        """
        証券会社の削除
        
        Args:
            broker: 証券会社名
        
        Returns:
            成功時True、失敗時False
        """
        if broker in self.brokers:
            self.brokers.remove(broker)
            return self._save_master()
        else:
            print(f"証券会社 '{broker}' が見つかりません")
            return False
    
    # ========== カテゴリ・地域取得 ==========
    
    def get_categories(self) -> List[str]:
        """登録されている全カテゴリの取得"""
        return sorted(set(b.get('category', 'その他') for b in self.brands))
    
    def get_regions(self) -> List[str]:
        """登録されている全地域の取得"""
        return sorted(set(b.get('region', 'その他') for b in self.brands))
    
    def get_accounts(self) -> List[str]:
        """登録されている全口座種別の取得"""
        accounts = set(b.get('account', '特定') for b in self.brands)
        # 標準的な口座種別を優先順で返す
        standard_accounts = ['積立NISA', 'NISA', '特定']
        result = [acc for acc in standard_accounts if acc in accounts]
        # その他の口座種別を追加
        result.extend(sorted(acc for acc in accounts if acc not in standard_accounts))
        return result
    
    # ========== 一括操作 ==========
    
    def import_from_dataframe(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        DataFrameから銘柄・投資方法・証券会社を一括インポート
        
        Args:
            df: 投資データDataFrame（'銘柄', '投資方法', '証券会社'カラム）
        
        Returns:
            インポート結果（各項目の追加数）
        """
        result = {'brands': 0, 'methods': 0, 'brokers': 0}
        
        # 銘柄のインポート（カンマ区切り対応）
        if '銘柄' in df.columns:
            brands_raw = df['銘柄'].dropna().astype(str).tolist()
            for brand_str in brands_raw:
                for code in brand_str.split(','):
                    code = code.strip()
                    if code and not any(b['code'] == code for b in self.brands):
                        # コードのみの場合、名前も同じにする
                        self.brands.append({
                            'code': code,
                            'name': code,
                            'broker': '',
                            'account': '特定',
                            'category': 'その他',
                            'region': 'その他',
                            'created_at': datetime.now().isoformat()
                        })
                        result['brands'] += 1
        
        # 投資方法のインポート
        if '投資方法' in df.columns:
            methods_raw = df['投資方法'].dropna().astype(str).unique().tolist()
            for method in methods_raw:
                if method and method not in self.methods:
                    self.methods.append(method)
                    result['methods'] += 1
        
        # 証券会社のインポート
        if '証券会社' in df.columns:
            brokers_raw = df['証券会社'].dropna().astype(str).unique().tolist()
            for broker in brokers_raw:
                if broker and broker not in self.brokers:
                    self.brokers.append(broker)
                    result['brokers'] += 1
        
        if result['brands'] > 0 or result['methods'] > 0 or result['brokers'] > 0:
            self._save_master()
        
        return result
    
    def reset_to_default(self):
        """マスタデータをデフォルトにリセット"""
        self._initialize_default_data()


# モジュールレベルのシングルトンインスタンス
_master_instance: Optional[BrandMaster] = None


def get_brand_master() -> BrandMaster:
    """
    銘柄マスタのシングルトンインスタンスを取得
    
    Returns:
        BrandMasterインスタンス
    """
    global _master_instance
    if _master_instance is None:
        _master_instance = BrandMaster()
    return _master_instance
