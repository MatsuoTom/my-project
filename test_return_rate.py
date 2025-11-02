import pandas as pd
import sys
sys.path.append('.')

from investment_simulation.analysis.sbi_csv_parser import SBICSVParser
from investment_simulation.analysis.performance_analyzer import PerformanceAnalyzer

# サンプルデータを読み込み
parser = SBICSVParser()
parser.load_csv('investment_simulation/data/sample_sbi_emaxis_slim_sp500.csv')
parser.parse_data()

df = parser.parsed_data

print("=== データ概要 ===")
print(f"レコード数: {len(df)}")
print(f"口座種別: {df['口座種別'].unique()}")
print()

# 最初の数レコードを確認
print("=== 最初の5レコード ===")
print(df[['発生日', '取引区分', '口座種別', '金額(円)', '数量(口)', '当日基準価額', '保有数量', '評価金額', '個別元本']].head(5))
print()

# PerformanceAnalyzerで累計指標を計算
analyzer = PerformanceAnalyzer(df)
cumulative_df = analyzer.calculate_cumulative_metrics()

print("=== 累計指標（最初の10レコード） ===")
print(cumulative_df[['発生日', '取引区分', '累計投資額', '累計評価額', '累計損益', '累計リターン率']].head(10))
print()

print("=== 累計指標（最後の5レコード） ===")
print(cumulative_df[['発生日', '取引区分', '累計投資額', '累計評価額', '累計損益', '累計リターン率']].tail(5))
print()

# 基本統計
stats = parser.get_basic_stats()
print("=== 基本統計 ===")
print(f"総投資額: ¥{stats['総投資額']:,.0f}")
print(f"現在評価額: ¥{stats['現在評価額']:,.0f}")
print(f"総合損益: ¥{stats['総合損益']:,.0f}")
print(f"総合リターン率: {stats['総合リターン率']:.2f}%")
print(f"CAGR: {stats['年率換算リターン_CAGR']:.2f}%")
