"""
年金計算ユーティリティ

年金データの管理と計算を行うメインモジュール

Phase 3: 共通基盤（common/）との統合準備
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import List, Dict, Tuple, Optional
import os
from common.calculators.base_calculator import BaseFinancialCalculator
from common.utils.date_utils import calculate_age

# サンプルデータ（実際のプロジェクトでは外部データを使用）
SAMPLE_PENSION_RECORDS = [
    {"年度": 2011, "年齢": 20, "加入制度": "国民年金", "お勤め先": "第1号被保険者", "加入月数": 3, "納付額": 45060, "推定年収": 0},
    {"年度": 2012, "年齢": 21, "加入制度": "国民年金", "お勤め先": "第1号被保険者", "加入月数": 12, "納付額": 179760, "推定年収": 0},
    {"年度": 2013, "年齢": 22, "加入制度": "国民年金", "お勤め先": "第1号被保険者", "加入月数": 12, "納付額": 180480, "推定年収": 0},
    {"年度": 2014, "年齢": 23, "加入制度": "国民年金", "お勤め先": "第1号被保険者", "加入月数": 12, "納付額": 183000, "推定年収": 0},
    {"年度": 2015, "年齢": 24, "加入制度": "国民年金", "お勤め先": "第1号被保険者", "加入月数": 12, "納付額": 187080, "推定年収": 0},
    {"年度": 2016, "年齢": 25, "加入制度": "厚生年金", "お勤め先": "トヨタ自動車株式会社", "加入月数": 12, "納付額": 133422, "推定年収": 3368599},
    {"年度": 2017, "年齢": 26, "加入制度": "厚生年金", "お勤め先": "トヨタ自動車株式会社", "加入月数": 12, "納付額": 452947, "推定年収": 5452518},
    {"年度": 2018, "年齢": 27, "加入制度": "厚生年金", "お勤め先": "トヨタ自動車株式会社", "加入月数": 12, "納付額": 515785, "推定年収": 5606908},
    {"年度": 2019, "年齢": 28, "加入制度": "厚生年金", "お勤め先": "トヨタ自動車株式会社", "加入月数": 12, "納付額": 514870, "推定年収": 5540168},
    {"年度": 2020, "年齢": 29, "加入制度": "厚生年金", "お勤め先": "トヨタ自動車株式会社", "加入月数": 12, "納付額": 566202, "推定年収": 6785172},
    {"年度": 2021, "年齢": 30, "加入制度": "厚生年金", "お勤め先": "トヨタ自動車株式会社", "加入月数": 12, "納付額": 632082, "推定年収": 1290700},
    {"年度": 2022, "年齢": 31, "加入制度": "厚生年金", "お勤め先": "トヨタ自動車株式会社", "加入月数": 12, "納付額": 625676, "推定年収": 7173496},
    {"年度": 2023, "年齢": 32, "加入制度": "厚生年金", "お勤め先": "トヨタ自動車株式会社", "加入月数": 12, "納付額": 751581, "推定年収": 8698508},
    {"年度": 2024, "年齢": 33, "加入制度": "厚生年金", "お勤め先": "トヨタ自動車株式会社", "加入月数": 12, "納付額": 839878, "推定年収": 11562174},
]

# 実績年収データ
ACTUAL_SALARY_HISTORY = {
    2020: 4000000,
    2021: 4200000,
    2022: 4400000,
    2023: 4600000,
}

# 国民年金保険料履歴
DEFAULT_NATIONAL_PENSION_HISTORY = [
    {"年度": 2020, "月額保険料": 16540},
    {"年度": 2021, "月額保険料": 16610},
    {"年度": 2022, "月額保険料": 16590},
    {"年度": 2023, "月額保険料": 16520},
]

# データスキーマと保存先
DATA_COLUMNS = ["年度", "年齢", "加入制度", "お勤め先", "加入月数", "納付額", "推定年収"]
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
RECORDS_CSV_PATH = os.path.join(DATA_DIR, "pension_records.csv")

def _ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

def _coerce_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df.copy()
    # 必須列を揃える
    for col in DATA_COLUMNS:
        if col not in df2.columns:
            df2[col] = pd.Series([None] * len(df2))
    df2 = df2[DATA_COLUMNS]
    # 数値列の型変換
    for col in ["年度", "年齢", "加入月数", "納付額", "推定年収"]:
        df2[col] = pd.to_numeric(df2[col], errors="coerce").astype("Int64")
    # 文字列列
    df2["加入制度"] = df2["加入制度"].astype("string")
    df2["お勤め先"] = df2["お勤め先"].astype("string")
    # 欠損を 0 に置換（数値列）
    for col in ["加入月数", "納付額", "推定年収"]:
        df2[col] = df2[col].fillna(0)
    return df2

# 実績年収（バックアップ互換の定数）
ACTUAL_SALARY_HISTORY_START_YEAR = 2016
ACTUAL_SALARY_HISTORY = [
    3368599, 5452518, 5606908, 5540168, 6785172, 1290700, 7173496, 8698508, 11562174
]

def get_career_model(kind: str = "default", to_yen: bool = False) -> pd.DataFrame:
    """キャリアモデル（バックアップ互換）"""
    models = {
        "default": [
            {"年齢": 30, "役職": "指導職", "推定年収(万円)": 850},
            {"年齢": 35, "役職": "主任", "推定年収(万円)": 1150},
            {"年齢": 40, "役職": "基幹職", "推定年収(万円)": 1280},
            {"年齢": 45, "役職": "基幹職", "推定年収(万円)": 1380},
            {"年齢": 50, "役職": "基幹職", "推定年収(万円)": 1430},
            {"年齢": 55, "役職": "定年退職", "推定年収(万円)": 1480},
            {"年齢": 56, "役職": "出向(60%)", "推定年収(万円)": 888},
            {"年齢": 60, "役職": "完全退職", "推定年収(万円)": 888},
        ],
        "expanded": [
            {"年齢": 25, "役職": "新卒/若手", "推定年収(万円)": 450},
            {"年齢": 28, "役職": "若手", "推定年収(万円)": 550},
            {"年齢": 30, "役職": "指導職", "推定年収(万円)": 850},
            {"年齢": 33, "役職": "主任候補", "推定年収(万円)": 1000},
            {"年齢": 35, "役職": "主任", "推定年収(万円)": 1150},
            {"年齢": 38, "役職": "上級主任", "推定年収(万円)": 1220},
            {"年齢": 40, "役職": "基幹職", "推定年収(万円)": 1280},
            {"年齢": 45, "役職": "課長/基幹職", "推定年収(万円)": 1380},
            {"年齢": 50, "役職": "部長", "推定年収(万円)": 1600},
            {"年齢": 55, "役職": "定年退職", "推定年収(万円)": 1700},
            {"年齢": 60, "役職": "完全退職", "推定年収(万円)": 1020},
        ],
    }
    data = models.get(kind, models["default"])
    df_model = pd.DataFrame(data)
    if to_yen:
        df_model["推定年収(円)"] = (df_model["推定年収(万円)"] * 10000).astype(int)
    return df_model

def load_df_from_csv() -> Optional[pd.DataFrame]:
    if os.path.exists(RECORDS_CSV_PATH):
        try:
            df_csv = pd.read_csv(RECORDS_CSV_PATH, encoding="utf-8")
            return _coerce_dtypes(df_csv)
        except Exception:
            return None
    return None

def save_df(new_df: pd.DataFrame) -> None:
    """レコードをCSVへ保存し、モジュール内 df をインプレース更新する"""
    global df, records
    _ensure_data_dir()
    df_norm = _coerce_dtypes(new_df)
    # CSV 保存
    df_norm.to_csv(RECORDS_CSV_PATH, index=False, encoding="utf-8")
    # 既存 df を同一オブジェクトのまま更新
    if 'df' in globals() and isinstance(df, pd.DataFrame):
        # 列入れ替え・データ更新
        df.drop(df.index, inplace=True)
        # 既存列を合わせる
        for col in list(df.columns):
            if col not in df_norm.columns:
                df.drop(columns=[col], inplace=True, errors='ignore')
        for col in df_norm.columns:
            df[col] = df_norm[col].values
    else:
        df = df_norm.copy()
    # records も更新
    records.clear()
    records.extend(df_norm.astype(object).where(pd.notna(df_norm), None).to_dict(orient="records"))

class PensionCalculator(BaseFinancialCalculator):
    """
    年金計算メインクラス
    
    Phase 3で共通基盤（BaseFinancialCalculator）を継承。
    将来的な拡張（複利計算、現在価値計算等）に対応可能。
    """
    
    def __init__(self, records: List[Dict] = None):
        """
        初期化
        
        Args:
            records: 年金記録データのリスト
        """
        super().__init__()  # BaseFinancialCalculatorの初期化
        
        # 呼び出し元から明示的に渡されればそれを使用、なければ現在の df を利用
        if records is None:
            # 現在のグローバル df を使用（CSV読み込み後の最新状態）
            self.df = df.copy()
            self.records = self.df.to_dict(orient="records")
        else:
            self.records = records
            self.df = pd.DataFrame(self.records)
    
    def calculate(self, retirement_age: int = 65) -> Dict:
        """
        BaseFinancialCalculatorの抽象メソッド実装
        
        将来の年金受給額を計算します。
        
        Args:
            retirement_age: 退職年齢
            
        Returns:
            計算結果の辞書
        """
        return self.calculate_future_pension(retirement_age)
    
    def validate_inputs(self, retirement_age: int = 65) -> bool:
        """
        入力値の検証
        
        Args:
            retirement_age: 退職年齢
            
        Returns:
            bool: 検証結果
            
        Raises:
            ValueError: 不正な入力値の場合
        """
        if retirement_age < 60 or retirement_age > 75:
            raise ValueError("退職年齢は60歳から75歳の範囲である必要があります")
        
        if self.df is None or len(self.df) == 0:
            raise ValueError("年金記録データが空です")
        
        return True
    
    def calculate_future_pension(self, retirement_age: int = 65) -> Dict:
        """
        将来の年金受給額を計算
        
        Args:
            retirement_age: 退職年齢
            
        Returns:
            計算結果の辞書
        """
        total_contribution = self.df['納付額'].sum()
        total_months = self.df['加入月数'].sum()
        average_income = self.df['推定年収'].mean()
        
        # 簡易的な年金受給額計算
        basic_pension = 780900  # 基礎年金満額（令和5年度）
        employment_pension = average_income * 0.005481 * (total_months / 12)
        
        annual_pension = basic_pension + employment_pension
        
        return {
            "年間受給額": annual_pension,
            "月額受給額": annual_pension / 12,
            "総納付額": total_contribution,
            "加入月数": total_months,
            "平均年収": average_income,
            "受給開始年齢": retirement_age
        }
    
    def analyze_contribution_efficiency(self) -> Dict:
        """
        納付効率性を分析
        
        Returns:
            分析結果の辞書
        """
        pension_result = self.calculate_future_pension()
        total_contribution = pension_result["総納付額"]
        annual_pension = pension_result["年間受給額"]
        
        # 損益分岐点計算（何年で元が取れるか）
        breakeven_years = total_contribution / annual_pension if annual_pension > 0 else float('inf')
        
        return {
            "損益分岐年数": breakeven_years,
            "年間利回り相当": (annual_pension / total_contribution) * 100 if total_contribution > 0 else 0,
            "総納付額": total_contribution,
            "年間受給額": annual_pension
        }

def build_paid_years(start_year: int = 2020, years: int = 4) -> List[int]:
    """
    納付年度のリストを生成
    
    Args:
        start_year: 開始年度
        years: 年数
        
    Returns:
        年度のリスト
    """
    return list(range(start_year, start_year + years))

def estimate_income_by_company_growth(
    base_income: int = 4000000, 
    growth_rate: float = 0.05, 
    years: int = 4
) -> List[int]:
    """
    企業成長率を考慮した年収推定
    
    Args:
        base_income: 基準年収
        growth_rate: 成長率
        years: 推定年数
        
    Returns:
        推定年収のリスト
    """
    incomes = []
    current_income = base_income
    
    for _ in range(years):
        incomes.append(int(current_income))
        current_income *= (1 + growth_rate)
    
    return incomes

def paid_months_kokumin(years: int = 4, months_per_year: int = 12) -> int:
    """
    国民年金の納付月数を計算
    
    Args:
        years: 年数
        months_per_year: 年間月数
        
    Returns:
        総納付月数
    """
    return years * months_per_year

def past_insured_months() -> int:
    """
    過去の被保険者月数を取得
    
    Returns:
        過去の被保険者月数
    """
    # サンプルデータから計算
    return sum(record["加入月数"] for record in SAMPLE_PENSION_RECORDS)

def generate_national_pension_projection(growth_rate: float = 0.01) -> Tuple:
    """
    国民年金の将来予測を生成
    
    Args:
        growth_rate: 保険料成長率
        
    Returns:
        (実績年数, 国民年金履歴, 将来年数, 将来月額保険料)のタプル
    """
    history = DEFAULT_NATIONAL_PENSION_HISTORY
    years_actual = [h["年度"] for h in history]
    national_history = [h["月額保険料"] for h in history]
    
    # 将来予測（5年分）
    future_years = list(range(2024, 2029))
    last_fee = national_history[-1]
    future_monthly_fees = []
    
    for i, year in enumerate(future_years):
        future_fee = int(last_fee * ((1 + growth_rate) ** (i + 1)))
        future_monthly_fees.append(future_fee)
    
    return years_actual, national_history, future_years, future_monthly_fees

def apply_actual_salary_to_df(
    df: pd.DataFrame, 
    start_year: int = 2020, 
    values: List[int] = None
) -> pd.DataFrame:
    """
    実績年収をDataFrameに適用
    
    Args:
        df: 対象DataFrame
        start_year: 開始年度
        values: 実績年収のリスト
        
    Returns:
        更新されたDataFrame
    """
    if values is None:
        values = list(ACTUAL_SALARY_HISTORY.values())
    
    df_updated = df.copy()
    
    for i, value in enumerate(values):
        year = start_year + i
        mask = df_updated["年度"] == year
        if mask.any():
            df_updated.loc[mask, "推定年収"] = value
    
    return df_updated

# メインデータフレーム（グローバルで使用）
_loaded = load_df_from_csv()
if _loaded is not None and len(_loaded) > 0:
    df = _loaded
else:
    df = pd.DataFrame(SAMPLE_PENSION_RECORDS)
records = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")