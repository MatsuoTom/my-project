def add_bulk_records(df, bulk_df):
    """
    複数行DataFrame（年,月,銘柄,投資方法,証券会社,投資額,評価額,備考）を一括追加
    """
    for _, row in bulk_df.iterrows():
        # 必須項目が空欄ならスキップ
        if not (str(row.get("銘柄", "")).strip() and str(row.get("投資方法", "")).strip() and str(row.get("証券会社", "")).strip()):
            continue
        df = add_monthly_record(
            df,
            int(row["年"]),
            int(row["月"]),
            float(row["投資額"]),
            float(row["評価額"]),
            brands=str(row["銘柄"]),
            note=str(row["備考"]),
            method=str(row["投資方法"]),
            broker=str(row["証券会社"])
        )
    return df
"""
NISA投資シミュレーション・データ管理ユーティリティ

このモジュールはNISAの月次投資データの管理、分析、永続化機能を提供します。
- 月次データ（投資額、評価額、損益）の管理
- CSV形式でのデータ保存・読込
- 基本的な投資計算機能
- データ検証・フォーマット機能
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Union
import os

# データディレクトリの設定
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# デフォルトのCSVファイルパス
DEFAULT_NISA_CSV = DATA_DIR / "nisa_monthly_data.csv"

def get_default_nisa_data() -> pd.DataFrame:
    """
    デフォルトのNISA月次データを生成
    
    Returns:
        pd.DataFrame: デフォルトのNISA月次データ
    """
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # 過去12ヶ月のサンプルデータ
    data = []
    for i in range(12):
        year = current_year if i < current_month else current_year - 1
        month = (current_month - i) if i < current_month else (12 + current_month - i)
        data.append({
            '年': year,
            '月': month,
            '銘柄': '',  # ユーザーが入力（複数の場合はカンマ区切り文字列）
            '投資方法': '',  # 新規追加: ユーザーが入力
            '投資額': 0,  # ユーザーが入力
                '銘柄': '',  # ユーザーが入力（複数の場合はカンマ区切り文字列）
                '投資方法': '',  # ユーザーが入力
                '証券会社': '',  # 新規追加: ユーザーが入力
            '累計評価額': 0,  # 計算される
            '損益': 0,  # 計算される
            '累計損益': 0,  # 計算される
            '損益率': 0.0,  # 計算される（%）
            '備考': ''
        })
    
    # 新しい順にソート
    data.reverse()
    df = pd.DataFrame(data)
    return df

def calculate_cumulative_values(df: pd.DataFrame) -> pd.DataFrame:
    df = df.reset_index(drop=True)
    """
    累計値と損益を計算
    """
    df['累計投資額'] = df['投資額'].cumsum()
    df['累計評価額'] = df['累計投資額'] - df['累計投資額'] + df['評価額'].cumsum()
    
    # 実際の累計評価額を正しく計算（前月までの評価額 + 今月の新規投資額と評価額の差）
    cumulative_evaluation = 0
    for i in range(len(df)):
        if i == 0:
            cumulative_evaluation = df.loc[i, '評価額']
        else:
            # 前月の累計評価額 + 今月の投資額 + 今月の増減
            monthly_change = df.loc[i, '評価額'] - df.loc[i, '投資額']
            cumulative_evaluation += df.loc[i, '投資額'] + monthly_change
        
        df.loc[i, '累計評価額'] = cumulative_evaluation
    
    # 損益計算
    df['損益'] = df['評価額'] - df['投資額']
    df['累計損益'] = df['累計評価額'] - df['累計投資額']
    
    # 損益率計算（累計投資額が0でないときのみ）
    df['損益率'] = 0.0
    mask = df['累計投資額'] > 0
    df.loc[mask, '損益率'] = (df.loc[mask, '累計損益'] / df.loc[mask, '累計投資額']) * 100
    
    return df

def save_nisa_data(df: pd.DataFrame, filepath: Optional[Union[str, Path]] = None) -> bool:
    """
    NISAデータをCSVファイルに保存
    
    Args:
        df (pd.DataFrame): 保存するデータ
        filepath (Optional[Union[str, Path]]): 保存先ファイルパス
        
    Returns:
        bool: 保存成功時True
    """
    try:
        if filepath is None:
            filepath = DEFAULT_NISA_CSV
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # 累計値を再計算してから保存
        df_calc = calculate_cumulative_values(df)
        df_calc.to_csv(filepath, index=False, encoding='utf-8-sig')
        return True
    except Exception as e:
        print(f"データ保存エラー: {e}")
        return False

def load_nisa_data(filepath: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """
    CSVファイルからNISAデータを読み込み
    
    Args:
        filepath (Optional[Union[str, Path]]): 読み込み元ファイルパス
        
    Returns:
        pd.DataFrame: 読み込んだデータ（読み込み失敗時はデフォルトデータ）
    """
    try:
        if filepath is None:
            filepath = DEFAULT_NISA_CSV
        
        filepath = Path(filepath)
        if not filepath.exists():
            print(f"ファイルが存在しません: {filepath}")
            return get_default_nisa_data()
        
        df = pd.read_csv(filepath, encoding='utf-8-sig')
        
        # 必要なカラムの存在確認と追加
        required_columns = ['年', '月', '銘柄', '投資方法', '投資額', '評価額', '累計投資額', '累計評価額', '損益', '累計損益', '損益率', '備考']
        for col in required_columns:
            if col not in df.columns:
                if col in ['投資額', '評価額', '累計投資額', '累計評価額', '損益', '累計損益']:
                    df[col] = 0
                elif col == '損益率':
                    df[col] = 0.0
                else:
                    df[col] = ''
        
        # データ型の調整
        numeric_columns = ['年', '月', '投資額', '評価額', '累計投資額', '累計評価額', '損益', '累計損益', '損益率']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # 累計値を再計算
        df = calculate_cumulative_values(df)
        
        return df
        
    except Exception as e:
        print(f"データ読み込みエラー: {e}")
        return get_default_nisa_data()

def add_monthly_record(df: pd.DataFrame, year: int, month: int, investment: float, evaluation: float, note: str = '', brands: Union[str, list] = '', method: str = '', broker: str = '') -> pd.DataFrame:
    """
    月次記録を追加
    
    Args:
        df (pd.DataFrame): 既存のデータ
        year (int): 年
        month (int): 月
        investment (float): 投資額
        evaluation (float): 評価額
        note (str): 備考
        
    Returns:
        pd.DataFrame: 更新されたデータ
    """
    # brands: str（カンマ区切り）またはList[str]
    if isinstance(brands, list):
        brands_str = ','.join([b.strip() for b in brands if b.strip()])
    else:
        brands_str = str(brands).strip()
    new_record = {
        '年': year,
        '月': month,
        '銘柄': brands_str,  # 複数の場合はカンマ区切り文字列
            '投資方法': method,  # ユーザーが入力
            '証券会社': broker,  # ユーザーが入力
        '投資額': investment,
        '評価額': evaluation,
        '累計投資額': 0,  # 後で計算
        '累計評価額': 0,  # 後で計算
        '損益': 0,  # 後で計算
        '累計損益': 0,  # 後で計算
        '損益率': 0.0,  # 後で計算
        '備考': note
    }
    # 既存レコードがあるかチェック
    mask = (df['年'] == year) & (df['月'] == month)
    if mask.any():
        # 既存レコードを更新
        df.loc[mask, '投資額'] = investment
        df.loc[mask, '評価額'] = evaluation
        df.loc[mask, '備考'] = note
        if brands_str:
            df.loc[mask, '銘柄'] = brands_str
            if method:
                df.loc[mask, '投資方法'] = method
            if broker:
                df.loc[mask, '証券会社'] = broker
    else:
        # 新規レコードを追加
        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    # 累計値を再計算
    df = calculate_cumulative_values(df)
    return df

def get_investment_summary(df: pd.DataFrame) -> Dict[str, float]:
    """
    投資サマリー情報を取得
    
    Args:
        df (pd.DataFrame): NISAデータ
        
    Returns:
        Dict[str, float]: サマリー情報
    """
    if df.empty:
        return {
            'total_investment': 0,
            'total_evaluation': 0,
            'total_profit_loss': 0,
            'profit_loss_rate': 0.0,
            'monthly_avg_investment': 0,
            'months_count': 0
        }
    
    # データをソートして最新の累計値を取得
    df_sorted = df.sort_values(['年', '月'])
    latest = df_sorted.iloc[-1] if not df_sorted.empty else df_sorted
    
    # 月次データのカウント（投資額が0より大きいもの）
    active_months = len(df[df['投資額'] > 0])
    
    summary = {
        'total_investment': float(latest['累計投資額']),
        'total_evaluation': float(latest['累計評価額']),
        'total_profit_loss': float(latest['累計損益']),
        'profit_loss_rate': float(latest['損益率']),
        'monthly_avg_investment': float(df[df['投資額'] > 0]['投資額'].mean()) if active_months > 0 else 0,
        'months_count': active_months
    }
    
    return summary

def validate_nisa_data(df: pd.DataFrame) -> List[str]:
    """
    NISAデータの妥当性をチェック
    
    Args:
        df (pd.DataFrame): チェック対象のデータ
        
    Returns:
        List[str]: エラーメッセージのリスト（エラーがない場合は空リスト）
    """
    errors = []
    
    if df.empty:
        errors.append("データが空です")
        return errors
    
    # 必要なカラムの存在確認
    required_columns = ['年', '月', '投資額', '評価額']
    for col in required_columns:
            required_columns = ['年', '月', '銘柄', '投資方法', '証券会社', '投資額', '評価額', '累計投資額', '累計評価額', '損益', '累計損益', '損益率', '備考']
            errors.append(f"必要なカラムが不足しています: {col}")
    
    # 数値データの妥当性チェック
    for idx, row in df.iterrows():
        try:
            year = int(row['年'])
            month = int(row['月'])
            
            if year < 2000 or year > 2100:
                errors.append(f"行{idx+1}: 年が範囲外です ({year})")
            
            if month < 1 or month > 12:
                errors.append(f"行{idx+1}: 月が範囲外です ({month})")
            
            if row['投資額'] < 0:
                errors.append(f"行{idx+1}: 投資額が負の値です")
            
        except (ValueError, TypeError):
            errors.append(f"行{idx+1}: 数値データが不正です")
    
    return errors

class NISACalculator:
    """NISA投資計算クラス"""
    
    def __init__(self, df: pd.DataFrame):
        """
        初期化
        
        Args:
            df (pd.DataFrame): NISAデータ
        """
        self.df = df.copy()
    
    def calculate_annual_return(self) -> float:
        """
        年間リターン率を計算（CAGR: 複合年間成長率）
        
        Returns:
            float: 年間リターン率（%）
        """
        if self.df.empty or len(self.df) < 2:
            return 0.0
        
        df_sorted = self.df.sort_values(['年', '月'])
        
        # 期間を計算（月数）
        start_row = df_sorted.iloc[0]
        end_row = df_sorted.iloc[-1]
        
        start_date = datetime(int(start_row['年']), int(start_row['月']), 1)
        end_date = datetime(int(end_row['年']), int(end_row['月']), 1)
        
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        if months <= 0:
            return 0.0
        
        years = months / 12
        
        # 初期投資額と最終評価額
        initial_value = float(df_sorted.iloc[0]['累計投資額'])
        final_value = float(end_row['累計評価額'])
        
        if initial_value <= 0 or final_value <= 0:
            return 0.0
        
        # CAGR計算
        cagr = ((final_value / initial_value) ** (1 / years) - 1) * 100
        
        return cagr
    
    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.1) -> float:
        """
        シャープレシオを計算
        
        Args:
            risk_free_rate (float): リスクフリーレート（%）
            
        Returns:
            float: シャープレシオ
        """
        if len(self.df) < 2:
            return 0.0
        
        # 月次リターンを計算
        df_sorted = self.df.sort_values(['年', '月'])
        monthly_returns = []
        
        for i in range(1, len(df_sorted)):
            prev_value = df_sorted.iloc[i-1]['累計評価額']
            curr_value = df_sorted.iloc[i]['累計評価額']
            
            if prev_value > 0:
                monthly_return = (curr_value - prev_value) / prev_value
                monthly_returns.append(monthly_return)
        
        if not monthly_returns:
            return 0.0
        
        # 平均リターンと標準偏差
        avg_return = np.mean(monthly_returns) * 12 * 100  # 年率換算（%）
        std_return = np.std(monthly_returns) * np.sqrt(12) * 100  # 年率換算（%）
        
        if std_return == 0:
            return 0.0
        
        # シャープレシオ
        sharpe = (avg_return - risk_free_rate) / std_return
        
        return sharpe
    
    def project_future_value(self, months: int, monthly_investment: float, expected_return: float) -> Dict[str, float]:
        """
        将来価値を予測
        
        Args:
            months (int): 予測期間（月数）
            monthly_investment (float): 月次投資額
            expected_return (float): 期待年間リターン率（%）
            
        Returns:
            Dict[str, float]: 予測結果
        """
        if self.df.empty:
            current_value = 0
            current_investment = 0
        else:
            df_sorted = self.df.sort_values(['年', '月'])
            latest = df_sorted.iloc[-1]
            current_value = float(latest['累計評価額'])
            current_investment = float(latest['累計投資額'])
        
        # 月次リターン率
        monthly_return = (expected_return / 100) / 12
        
        # 将来価値計算（複利効果を考慮）
        future_value = current_value
        total_investment = current_investment
        
        for month in range(months):
            # 既存資産の成長
            future_value = future_value * (1 + monthly_return)
            # 新規投資
            future_value += monthly_investment
            total_investment += monthly_investment
        
        projected_profit = future_value - total_investment
        projected_return_rate = (projected_profit / total_investment * 100) if total_investment > 0 else 0
        
        return {
            'future_value': future_value,
            'total_investment': total_investment,
            'projected_profit': projected_profit,
            'projected_return_rate': projected_return_rate
        }