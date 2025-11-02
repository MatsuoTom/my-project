"""
投資パフォーマンス分析モジュール

時系列分析、リターン計算、ドルコスト平均法の効果検証などを実施
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
import plotly.express as px


class PerformanceAnalyzer:
    """
    投資パフォーマンスを多角的に分析するクラス
    """
    
    def __init__(self, parsed_data: pd.DataFrame):
        """
        Args:
            parsed_data: SBICSVParserでパースされたDataFrame
        """
        self.data = parsed_data.copy()
        self.data = self.data.sort_values('発生日').reset_index(drop=True)
        
    def calculate_cumulative_metrics(self) -> pd.DataFrame:
        """
        累計指標を計算（投資額、評価額、損益など）
        
        Returns:
            pd.DataFrame: 累計指標付きデータ
        """
        df = self.data.copy()
        
        # 買付のみを対象に累計投資額を計算
        df['累計投資額'] = 0.0  # float型で初期化
        df['累計取得数量'] = 0.0  # float型で初期化
        
        cumulative_investment = 0.0
        cumulative_quantity = 0.0
        
        for idx in range(len(df)):
            if df.loc[idx, '取引区分'] == '買付':
                cumulative_investment += df.loc[idx, '金額(円)']
                cumulative_quantity += df.loc[idx, '数量(口)']
            elif df.loc[idx, '取引区分'] == '売却':
                # 売却時は投資額から差し引く（実現化）
                # 個別元本は1万口あたりの価格なので、実際の元本は: 数量 × 個別元本 / 10000
                sell_cost = (df.loc[idx, '数量(口)'] * df.loc[idx, '個別元本']) / 10000
                cumulative_investment -= sell_cost
                cumulative_quantity -= df.loc[idx, '数量(口)']
            
            df.loc[idx, '累計投資額'] = cumulative_investment
            df.loc[idx, '累計取得数量'] = cumulative_quantity
        
        # 累計評価額（保有数量 × 当日基準価額）
        # 基準価額は1万口あたりの価格なので: 保有数量 × 基準価額 / 10000
        df['累計評価額'] = (df['保有数量'] * df['当日基準価額']) / 10000
        
        # 累計損益
        df['累計損益'] = df['累計評価額'] - df['累計投資額']
        
        # 累計リターン率（保有数量が0の場合はNaNとする）
        df['累計リターン率'] = 0.0
        # 累計投資額が正で、かつ保有数量が0より大きい場合のみ計算
        mask = (df['累計投資額'] > 0) & (df['保有数量'] > 0)
        df.loc[mask, '累計リターン率'] = (df.loc[mask, '累計損益'] / df.loc[mask, '累計投資額']) * 100
        
        # 保有数量が0の場合はNaNにする
        df.loc[df['保有数量'] == 0, '累計リターン率'] = float('nan')
        
        return df
    
    def analyze_dollar_cost_averaging(self) -> Dict:
        """
        ドルコスト平均法の効果を分析
        
        Returns:
            Dict: ドルコスト効果の分析結果
        """
        buy_df = self.data[self.data['取引区分'] == '買付'].copy()
        
        if len(buy_df) == 0:
            return {}
        
        # 平均取得単価
        total_quantity = buy_df['数量(口)'].sum()
        total_investment = buy_df['金額(円)'].sum()
        average_unit_cost = total_investment / total_quantity if total_quantity > 0 else 0
        
        # 各買付時の単価
        buy_df['取得単価'] = buy_df['金額(円)'] / buy_df['数量(口)']
        
        # 最終個別元本
        final_cost_basis = buy_df['個別元本'].iloc[-1]
        
        # 基準価額の統計
        price_stats = {
            '最高価格': buy_df['当日基準価額'].max(),
            '最低価格': buy_df['当日基準価額'].min(),
            '平均価格': buy_df['当日基準価額'].mean(),
            '価格変動率': (buy_df['当日基準価額'].std() / buy_df['当日基準価額'].mean()) * 100
        }
        
        # 高値掴み/安値拾い分析
        buy_df['価格順位'] = buy_df['当日基準価額'].rank(pct=True) * 100
        
        # 最高値での買付
        highest_price_buys = buy_df[buy_df['当日基準価額'] == price_stats['最高価格']]
        # 最低値での買付
        lowest_price_buys = buy_df[buy_df['当日基準価額'] == price_stats['最低価格']]
        
        return {
            '平均取得単価': average_unit_cost,
            '最終個別元本': final_cost_basis,
            '基準価額統計': price_stats,
            '最高値での買付回数': len(highest_price_buys),
            '最高値での買付額': highest_price_buys['金額(円)'].sum(),
            '最低値での買付回数': len(lowest_price_buys),
            '最低値での買付額': lowest_price_buys['金額(円)'].sum(),
            '取得単価分布': buy_df['取得単価'].describe().to_dict()
        }
    
    def compare_with_lump_sum(self) -> Dict:
        """
        一括投資との比較
        
        Returns:
            Dict: 比較結果
        """
        buy_df = self.data[self.data['取引区分'] == '買付'].copy()
        
        if len(buy_df) == 0:
            return {}
        
        total_investment = buy_df['金額(円)'].sum()
        first_buy_date = buy_df['発生日'].min()
        first_price = buy_df['当日基準価額'].iloc[0]
        latest_price = self.data['当日基準価額'].iloc[-1]
        
        # 一括投資の場合（初回に全額投資）
        lump_sum_quantity = total_investment / first_price
        lump_sum_value = lump_sum_quantity * latest_price
        lump_sum_return = ((lump_sum_value - total_investment) / total_investment) * 100
        
        # 実際の積立の場合
        actual_quantity = self.data['保有数量'].iloc[-1]
        actual_value = self.data['評価金額'].iloc[-1]
        actual_cost = self.data['累計投資額'].iloc[-1] if '累計投資額' in self.data.columns else total_investment
        actual_return = ((actual_value - actual_cost) / actual_cost) * 100 if actual_cost > 0 else 0
        
        return {
            '一括投資_初回価格': first_price,
            '一括投資_取得数量': lump_sum_quantity,
            '一括投資_評価額': lump_sum_value,
            '一括投資_リターン率': lump_sum_return,
            '積立投資_取得数量': actual_quantity,
            '積立投資_評価額': actual_value,
            '積立投資_リターン率': actual_return,
            '差異_数量': actual_quantity - lump_sum_quantity,
            '差異_評価額': actual_value - lump_sum_value,
            '差異_リターン率': actual_return - lump_sum_return
        }
    
    def calculate_best_worst_timing(self) -> Dict:
        """
        ベスト/ワーストタイミング分析
        
        Returns:
            Dict: タイミング分析結果
        """
        buy_df = self.data[self.data['取引区分'] == '買付'].copy()
        
        if len(buy_df) == 0:
            return {}
        
        # 各買付のその後のリターン
        results = []
        latest_price = self.data['当日基準価額'].iloc[-1]
        
        for idx, row in buy_df.iterrows():
            buy_price = row['当日基準価額']
            buy_amount = row['金額(円)']
            buy_date = row['発生日']
            
            # 現在価格でのリターン
            price_return = ((latest_price - buy_price) / buy_price) * 100
            value_return = (buy_amount * latest_price / buy_price) - buy_amount
            
            results.append({
                '買付日': buy_date,
                '買付価格': buy_price,
                '買付額': buy_amount,
                '現在価格比': price_return,
                '評価額差': value_return
            })
        
        results_df = pd.DataFrame(results)
        
        # ベスト5
        best_5 = results_df.nlargest(5, '現在価格比')
        # ワースト5
        worst_5 = results_df.nsmallest(5, '現在価格比')
        
        return {
            'ベストタイミング': best_5.to_dict('records'),
            'ワーストタイミング': worst_5.to_dict('records'),
            '平均リターン': results_df['現在価格比'].mean(),
            '中央値リターン': results_df['現在価格比'].median()
        }
    
    def plot_cumulative_performance(self, by_account: bool = False) -> go.Figure:
        """
        累計パフォーマンスをプロット
        
        Args:
            by_account: 口座別に分けて表示するか
            
        Returns:
            plotly.graph_objects.Figure: グラフオブジェクト
        """
        df = self.calculate_cumulative_metrics()
        
        fig = go.Figure()
        
        if by_account and '口座種別' in df.columns:
            # 口座別に集計
            accounts = df['口座種別'].unique()
            
            for account in accounts:
                account_df = df[df['口座種別'] == account].copy()
                
                # 口座別の累計を再計算
                cumulative_investment = 0.0
                cumulative_value = []
                cumulative_inv = []
                
                for idx in account_df.index:
                    if account_df.loc[idx, '取引区分'] == '買付':
                        cumulative_investment += account_df.loc[idx, '金額(円)']
                    elif account_df.loc[idx, '取引区分'] == '売却':
                        sell_cost = (account_df.loc[idx, '数量(口)'] * account_df.loc[idx, '個別元本']) / 10000
                        cumulative_investment -= sell_cost
                    
                    cumulative_inv.append(cumulative_investment)
                    cumulative_value.append((account_df.loc[idx, '保有数量'] * account_df.loc[idx, '当日基準価額']) / 10000)
                
                # 投資額（万円単位に変換）
                fig.add_trace(go.Scatter(
                    x=account_df['発生日'],
                    y=[v / 10000 for v in cumulative_inv],
                    mode='lines',
                    name=f'{account} - 投資額',
                    line=dict(width=2, dash='dot'),
                    hovertemplate='%{y:.1f}万円<extra></extra>'
                ))
                
                # 評価額（万円単位に変換）
                fig.add_trace(go.Scatter(
                    x=account_df['発生日'],
                    y=[v / 10000 for v in cumulative_value],
                    mode='lines',
                    name=f'{account} - 評価額',
                    line=dict(width=2),
                    hovertemplate='%{y:.1f}万円<extra></extra>'
                ))
        else:
            # 全体の累計（万円単位に変換）
            # 累計投資額
            fig.add_trace(go.Scatter(
                x=df['発生日'],
                y=df['累計投資額'] / 10000,
                mode='lines',
                name='累計投資額',
                line=dict(color='blue', width=2),
                hovertemplate='%{y:.1f}万円<extra></extra>'
            ))
            
            # 累計評価額
            fig.add_trace(go.Scatter(
                x=df['発生日'],
                y=df['累計評価額'] / 10000,
                mode='lines',
                name='累計評価額',
                line=dict(color='green', width=2),
                hovertemplate='%{y:.1f}万円<extra></extra>'
            ))
        
        fig.update_layout(
            title='累計投資額 vs 累計評価額' + (' (口座別)' if by_account else ''),
            xaxis_title='日付',
            yaxis_title='金額（万円）',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def plot_return_rate(self, by_account: bool = False) -> go.Figure:
        """
        リターン率の推移をプロット
        
        Args:
            by_account: 口座別に分けて表示するか
            
        Returns:
            plotly.graph_objects.Figure: グラフオブジェクト
        """
        df = self.calculate_cumulative_metrics()
        
        fig = go.Figure()
        
        if by_account and '口座種別' in df.columns:
            # 口座別に集計
            accounts = df['口座種別'].unique()
            
            for account in accounts:
                account_df = df[df['口座種別'] == account].copy()
                
                # 口座別の累計リターン率を再計算
                cumulative_investment = 0.0
                return_rates = []
                
                for idx in account_df.index:
                    if account_df.loc[idx, '取引区分'] == '買付':
                        cumulative_investment += account_df.loc[idx, '金額(円)']
                    elif account_df.loc[idx, '取引区分'] == '売却':
                        sell_cost = (account_df.loc[idx, '数量(口)'] * account_df.loc[idx, '個別元本']) / 10000
                        cumulative_investment -= sell_cost
                    
                    current_value = (account_df.loc[idx, '保有数量'] * account_df.loc[idx, '当日基準価額']) / 10000
                    
                    # 保有数量が0の場合はNaNを設定
                    if account_df.loc[idx, '保有数量'] == 0:
                        return_rate = float('nan')
                    elif cumulative_investment > 0:
                        return_rate = ((current_value - cumulative_investment) / cumulative_investment) * 100
                    else:
                        return_rate = 0.0
                    
                    return_rates.append(return_rate)
                
                fig.add_trace(go.Scatter(
                    x=account_df['発生日'],
                    y=return_rates,
                    mode='lines',
                    name=f'{account}',
                    line=dict(width=2),
                    fill='tozeroy',
                    fillcolor=f'rgba({hash(account) % 200}, {(hash(account) * 2) % 200}, {(hash(account) * 3) % 200}, 0.1)'
                ))
        else:
            # 全体のリターン率
            fig.add_trace(go.Scatter(
                x=df['発生日'],
                y=df['累計リターン率'],
                mode='lines',
                name='累計リターン率',
                line=dict(color='purple', width=2),
                fill='tozeroy',
                fillcolor='rgba(128, 0, 128, 0.1)'
            ))
        
        # ゼロラインを追加
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            title='累計リターン率の推移' + (' (口座別)' if by_account else ''),
            xaxis_title='日付',
            yaxis_title='リターン率（%）',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
        
        # ゼロラインを追加
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        fig.update_layout(
            title='累計リターン率の推移',
            xaxis_title='日付',
            yaxis_title='リターン率（%）',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def plot_unit_price_history(self) -> go.Figure:
        """
        基準価額の履歴をプロット（買付タイミングをマーク）
        
        Returns:
            plotly.graph_objects.Figure: グラフオブジェクト
        """
        fig = go.Figure()
        
        # 基準価額の推移
        fig.add_trace(go.Scatter(
            x=self.data['発生日'],
            y=self.data['当日基準価額'],
            mode='lines',
            name='基準価額',
            line=dict(color='orange', width=2)
        ))
        
        # 買付ポイント
        buy_df = self.data[self.data['取引区分'] == '買付']
        fig.add_trace(go.Scatter(
            x=buy_df['発生日'],
            y=buy_df['当日基準価額'],
            mode='markers',
            name='買付',
            marker=dict(color='blue', size=10, symbol='circle')
        ))
        
        # 売却ポイント
        sell_df = self.data[self.data['取引区分'] == '売却']
        if len(sell_df) > 0:
            fig.add_trace(go.Scatter(
                x=sell_df['発生日'],
                y=sell_df['当日基準価額'],
                mode='markers',
                name='売却',
                marker=dict(color='red', size=10, symbol='x')
            ))
        
        fig.update_layout(
            title='基準価額推移と取引タイミング',
            xaxis_title='日付',
            yaxis_title='基準価額（円）',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def plot_monthly_investment(self) -> go.Figure:
        """
        月次投資額をプロット
        
        Returns:
            plotly.graph_objects.Figure: グラフオブジェクト
        """
        buy_df = self.data[self.data['取引区分'] == '買付'].copy()
        
        # 年・月カラムが存在しない場合は作成
        if '年' not in buy_df.columns or '月' not in buy_df.columns:
            buy_df['年'] = buy_df['発生日'].dt.year
            buy_df['月'] = buy_df['発生日'].dt.month
        
        monthly = buy_df.groupby(['年', '月']).agg({
            '金額(円)': 'sum'
        }).reset_index()
        
        # 年月の日付を作成
        monthly['年月'] = pd.to_datetime(
            monthly['年'].astype(str) + '-' + monthly['月'].astype(str).str.zfill(2) + '-01'
        )
        
        fig = go.Figure()
        
        # 万円単位に変換
        fig.add_trace(go.Bar(
            x=monthly['年月'],
            y=monthly['金額(円)'] / 10000,
            name='月次投資額',
            marker_color='lightblue',
            hovertemplate='%{y:.1f}万円<extra></extra>'
        ))
        
        fig.update_layout(
            title='月次投資額の推移',
            xaxis_title='年月',
            yaxis_title='投資額（万円）',
            template='plotly_white',
            height=400
        )
        
        return fig
