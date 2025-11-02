"""
SBI証券CSV明細パーサー

SBI証券からダウンロードしたCSV明細を解析し、
構造化されたデータに変換します。
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SBICSVParser:
    """
    SBI証券のCSV明細をパース・解析するクラス
    
    対応フォーマット:
    - 発生日, 取引区分, 口座種別, 取引種別, 数量(口), 金額(円), 費用, 
      分配金内訳(普通分配金), 分配金内訳(特別分配金), 当日基準価額, 
      保有数量, 評価金額, 個別元本
    """
    
    def __init__(self):
        self.raw_data: Optional[pd.DataFrame] = None
        self.parsed_data: Optional[pd.DataFrame] = None
        self.buy_records: Optional[pd.DataFrame] = None
        self.sell_records: Optional[pd.DataFrame] = None
        
    def load_csv(self, filepath: str, encoding: str = 'shift-jis') -> pd.DataFrame:
        """
        CSVファイルを読み込み
        
        Args:
            filepath: CSVファイルパス
            encoding: 文字エンコーディング（デフォルト: shift-jis）
            
        Returns:
            pd.DataFrame: 読み込んだデータ
        """
        try:
            # まずshift-jisで試す
            df = pd.read_csv(filepath, encoding=encoding)
            self.raw_data = df.copy()
            return df
        except UnicodeDecodeError:
            # UTF-8でリトライ
            try:
                df = pd.read_csv(filepath, encoding='utf-8-sig')
                self.raw_data = df.copy()
                return df
            except Exception as e2:
                print(f"UTF-8でも読込失敗: {e2}")
                raise
    
    def parse_data(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        CSVデータを解析して構造化
        
        Args:
            df: 解析するDataFrame（Noneの場合はraw_dataを使用）
            
        Returns:
            pd.DataFrame: 解析済みデータ
        """
        if df is None:
            if self.raw_data is None:
                raise ValueError("データが読み込まれていません。先にload_csv()を実行してください。")
            df = self.raw_data.copy()
        
        # 日付型に変換
        df['発生日'] = pd.to_datetime(df['発生日'], format='%Y/%m/%d')
        
        # 数値型に変換（カンマ区切りを削除）
        numeric_cols = ['数量(口)', '金額(円)', '費用', '分配金内訳(普通分配金)', 
                       '分配金内訳(特別分配金)', '当日基準価額', '保有数量', 
                       '評価金額', '個別元本']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 年・月・年月カラムを追加
        df['年'] = df['発生日'].dt.year
        df['月'] = df['発生日'].dt.month
        df['年月'] = df['発生日'].dt.to_period('M')
        
        # 取引種別を分類
        df['取引分類'] = df['取引区分'].apply(self._classify_transaction)
        
        self.parsed_data = df
        
        # 買付・売却レコードを分離
        self.buy_records = df[df['取引区分'] == '買付'].copy()
        self.sell_records = df[df['取引区分'] == '売却'].copy()
        
        return df
    
    def _classify_transaction(self, transaction_type: str) -> str:
        """取引区分を分類"""
        if transaction_type == '買付':
            return '買付'
        elif transaction_type == '売却':
            return '売却'
        elif transaction_type == '分配金':
            return '分配金'
        else:
            return 'その他'
    
    def get_basic_stats(self) -> Dict:
        """
        基本統計情報を取得
        
        Returns:
            Dict: 統計情報の辞書
        """
        if self.parsed_data is None:
            raise ValueError("データが解析されていません。先にparse_data()を実行してください。")
        
        df = self.parsed_data
        
        # 買付データ
        buy_df = self.buy_records
        total_investment = buy_df['金額(円)'].sum() if len(buy_df) > 0 else 0
        buy_count = len(buy_df)
        
        # 売却データ
        sell_df = self.sell_records
        total_sell_amount = sell_df['金額(円)'].sum() if len(sell_df) > 0 else 0
        sell_count = len(sell_df)
        
        # 最新の保有情報
        latest_record = df.iloc[-1] if len(df) > 0 else None
        current_quantity = latest_record['保有数量'] if latest_record is not None else 0
        current_value = latest_record['評価金額'] if latest_record is not None else 0
        current_unit_price = latest_record['当日基準価額'] if latest_record is not None else 0
        current_cost_basis = latest_record['個別元本'] if latest_record is not None else 0
        
        # 実現損益（売却時）
        realized_pl = 0
        if len(sell_df) > 0:
            # 売却レコードの前の行から取得単価を推定
            for idx in sell_df.index:
                sell_amount = df.loc[idx, '金額(円)']
                sell_quantity = df.loc[idx, '数量(口)']
                
                # 前の行の個別元本を使用（1万口あたりの価格）
                if idx > 0:
                    prev_cost_basis = df.loc[idx - 1, '個別元本']
                    cost = (sell_quantity * prev_cost_basis) / 10000
                    realized_pl += (sell_amount - cost)
        
        # 含み損益
        if current_quantity > 0 and current_cost_basis > 0:
            # 個別元本は1万口あたりの価格
            cost = (current_quantity * current_cost_basis) / 10000
            unrealized_pl = current_value - cost
        else:
            unrealized_pl = 0
        
        # 総合損益
        total_pl = realized_pl + unrealized_pl
        
        # リターン率（実際の投資額に対する割合）
        net_investment = total_investment - total_sell_amount
        if net_investment > 0:
            total_return_rate = (total_pl / net_investment) * 100
        else:
            total_return_rate = 0
        
        # 保有期間
        if len(buy_df) > 0:
            first_buy_date = buy_df['発生日'].min()
            latest_date = df['発生日'].max()
            holding_days = (latest_date - first_buy_date).days
            holding_years = holding_days / 365.25
        else:
            holding_days = 0
            holding_years = 0
        
        # 年率換算リターン（CAGR）
        if holding_years > 0 and net_investment > 0:
            final_value = current_value + total_sell_amount
            cagr = (((final_value / total_investment) ** (1 / holding_years)) - 1) * 100
        else:
            cagr = 0
        
        return {
            '総投資額': total_investment,
            '買付回数': buy_count,
            '総売却額': total_sell_amount,
            '売却回数': sell_count,
            '現在保有数量': current_quantity,
            '現在評価額': current_value,
            '現在基準価額': current_unit_price,
            '個別元本': current_cost_basis,
            '実現損益': realized_pl,
            '含み損益': unrealized_pl,
            '総合損益': total_pl,
            '総合リターン率': total_return_rate,
            '保有期間_日数': holding_days,
            '保有期間_年数': holding_years,
            '年率換算リターン_CAGR': cagr,
            '最初の買付日': buy_df['発生日'].min() if len(buy_df) > 0 else None,
            '最終更新日': df['発生日'].max() if len(df) > 0 else None
        }
    
    def get_account_summary(self) -> pd.DataFrame:
        """
        口座種別ごとの集計
        
        Returns:
            pd.DataFrame: 口座別集計データ
        """
        if self.buy_records is None:
            raise ValueError("データが解析されていません。先にparse_data()を実行してください。")
        
        summary = self.buy_records.groupby('口座種別').agg({
            '金額(円)': 'sum',
            '数量(口)': 'sum',
            '発生日': 'count'
        }).reset_index()
        
        summary.columns = ['口座種別', '投資額', '保有数量', '買付回数']
        
        return summary
    
    def get_monthly_summary(self) -> pd.DataFrame:
        """
        月次の投資サマリー
        
        Returns:
            pd.DataFrame: 月次集計データ
        """
        if self.buy_records is None:
            raise ValueError("データが解析されていません。")
        
        monthly = self.buy_records.groupby(['年', '月']).agg({
            '金額(円)': 'sum',
            '数量(口)': 'sum',
            '当日基準価額': 'mean',
            '個別元本': 'last'
        }).reset_index()
        
        monthly.columns = ['年', '月', '投資額', '取得数量', '平均基準価額', '個別元本']
        
        # 年月の日付を作成
        monthly['年月'] = pd.to_datetime(
            monthly['年'].astype(str) + '-' + monthly['月'].astype(str).str.zfill(2) + '-01'
        )
        
        return monthly
    
    def get_time_series_data(self) -> pd.DataFrame:
        """
        時系列データ（全取引履歴）
        
        Returns:
            pd.DataFrame: 時系列データ
        """
        if self.parsed_data is None:
            raise ValueError("データが解析されていません。")
        
        return self.parsed_data.sort_values('発生日').copy()
    
    def export_summary(self, output_path: str):
        """
        サマリーをCSVで出力
        
        Args:
            output_path: 出力先ファイルパス
        """
        stats = self.get_basic_stats()
        account_summary = self.get_account_summary()
        monthly_summary = self.get_monthly_summary()
        
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            f.write("=== 基本統計情報 ===\n")
            for key, value in stats.items():
                f.write(f"{key}: {value}\n")
            
            f.write("\n=== 口座別集計 ===\n")
            account_summary.to_csv(f, index=False)
            
            f.write("\n=== 月次集計 ===\n")
            monthly_summary.to_csv(f, index=False)
        
        print(f"サマリーを {output_path} に出力しました。")
