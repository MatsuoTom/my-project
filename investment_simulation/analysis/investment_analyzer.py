"""
投資分析モジュール

NISA投資データの高度な分析機能を提供：
- リターン・リスク分析
- ポートフォリオ分析
- 複利効果の可視化
- 投資効率の評価
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import math

class InvestmentAnalyzer:
    """投資分析クラス"""
    
    def __init__(self, df: pd.DataFrame):
        """
        初期化
        
        Args:
            df (pd.DataFrame): NISAデータ
        """
        self.df = df.copy().sort_values(['年', '月'])
        self.monthly_data = self._prepare_monthly_analysis()
    
    def _prepare_monthly_analysis(self) -> pd.DataFrame:
        """月次分析用データを準備"""
        if self.df.empty:
            return pd.DataFrame()
        
        df = self.df.copy()
        
        # 月次リターン計算
        df['月次リターン'] = 0.0
        df['月次リターン率'] = 0.0
        
        for i in range(1, len(df)):
            prev_eval = df.iloc[i-1]['累計評価額']
            curr_eval = df.iloc[i]['累計評価額']
            curr_invest = df.iloc[i]['投資額']
            
            if prev_eval > 0:
                # 月次リターン = （今月評価額 - 前月評価額 - 今月投資額）/ 前月評価額
                monthly_return = (curr_eval - prev_eval - curr_invest) / prev_eval
                df.iloc[i, df.columns.get_loc('月次リターン')] = monthly_return
                df.iloc[i, df.columns.get_loc('月次リターン率')] = monthly_return * 100
        
        return df
    
    def calculate_risk_metrics(self) -> Dict[str, float]:
        """
        リスク指標を計算
        
        Returns:
            Dict[str, float]: リスク指標
        """
        if len(self.monthly_data) < 2:
            return {
                'volatility': 0.0,
                'max_drawdown': 0.0,
                'var_95': 0.0,
                'sharpe_ratio': 0.0,
                'calmar_ratio': 0.0
            }
        
        returns = self.monthly_data['月次リターン'].dropna()
        if len(returns) < 2:
            return {
                'volatility': 0.0,
                'max_drawdown': 0.0,
                'var_95': 0.0,
                'sharpe_ratio': 0.0,
                'calmar_ratio': 0.0
            }
        
        # ボラティリティ（年率）
        volatility = returns.std() * np.sqrt(12) * 100
        
        # 最大ドローダウン
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = abs(drawdown.min()) * 100
        
        # VaR（95%信頼区間）
        var_95 = abs(np.percentile(returns, 5)) * 100
        
        # シャープレシオ（リスクフリーレート0.1%想定）
        risk_free_rate = 0.001 / 12  # 月次リスクフリーレート
        excess_returns = returns - risk_free_rate
        sharpe_ratio = (excess_returns.mean() / returns.std() * np.sqrt(12)) if returns.std() > 0 else 0
        
        # カルマレシオ
        annual_return = returns.mean() * 12 * 100
        calmar_ratio = (annual_return / max_drawdown) if max_drawdown > 0 else 0
        
        return {
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'var_95': var_95,
            'sharpe_ratio': sharpe_ratio,
            'calmar_ratio': calmar_ratio
        }
    
    def analyze_investment_efficiency(self) -> Dict[str, float]:
        """
        投資効率を分析
        
        Returns:
            Dict[str, float]: 投資効率指標
        """
        if self.df.empty:
            return {
                'total_return_rate': 0.0,
                'annualized_return': 0.0,
                'cost_efficiency': 0.0,
                'investment_consistency': 0.0
            }
        
        latest = self.monthly_data.iloc[-1]
        total_investment = latest['累計投資額']
        total_evaluation = latest['累計評価額']
        
        # トータルリターン率
        total_return_rate = ((total_evaluation - total_investment) / total_investment * 100) if total_investment > 0 else 0
        
        # 年率換算リターン
        first_date = datetime(int(self.monthly_data.iloc[0]['年']), int(self.monthly_data.iloc[0]['月']), 1)
        last_date = datetime(int(latest['年']), int(latest['月']), 1)
        years = (last_date - first_date).days / 365.25
        
        annualized_return = 0.0
        if years > 0 and total_investment > 0 and total_evaluation > 0:
            annualized_return = ((total_evaluation / total_investment) ** (1 / years) - 1) * 100
        
        # コスト効率（投資額あたりの利益）
        cost_efficiency = (total_evaluation - total_investment) / len(self.monthly_data) if len(self.monthly_data) > 0 else 0
        
        # 投資一貫性（投資額の標準偏差の逆数）
        investment_amounts = self.monthly_data[self.monthly_data['投資額'] > 0]['投資額']
        investment_consistency = 1 / (investment_amounts.std() + 1) if len(investment_amounts) > 1 else 1
        
        return {
            'total_return_rate': total_return_rate,
            'annualized_return': annualized_return,
            'cost_efficiency': cost_efficiency,
            'investment_consistency': investment_consistency
        }
    
    def calculate_compound_interest_effect(self) -> Dict[str, any]:
        """
        複利効果を分析
        
        Returns:
            Dict[str, any]: 複利効果の分析結果
        """
        if len(self.monthly_data) < 2:
            return {
                'compound_benefit': 0.0,
                'simple_vs_compound': {'simple': 0.0, 'compound': 0.0},
                'monthly_compound_rates': []
            }
        
        # 月次複利率を計算
        monthly_rates = []
        compound_values = []
        simple_values = []
        
        cumulative_investment = 0
        compound_value = 0
        
        for i, row in self.monthly_data.iterrows():
            cumulative_investment += row['投資額']
            
            if i == 0:
                compound_value = row['評価額']
                simple_interest = 0
            else:
                # 複利効果を含む実際の評価額
                compound_value = row['累計評価額']
                
                # 単利で計算した場合の期待値（最初の月のリターン率を継続適用）
                if cumulative_investment > 0:
                    first_return_rate = (self.monthly_data.iloc[0]['評価額'] - self.monthly_data.iloc[0]['投資額']) / self.monthly_data.iloc[0]['投資額'] if self.monthly_data.iloc[0]['投資額'] > 0 else 0
                    simple_interest = cumulative_investment * first_return_rate * (i + 1)
                else:
                    simple_interest = 0
            
            simple_value = cumulative_investment + simple_interest
            
            compound_values.append(compound_value)
            simple_values.append(simple_value)
            
            # 月次複利率
            if cumulative_investment > 0:
                monthly_rate = ((compound_value - cumulative_investment) / cumulative_investment) * 100
                monthly_rates.append(monthly_rate)
            else:
                monthly_rates.append(0.0)
        
        # 複利の恩恵（複利 - 単利）
        final_compound = compound_values[-1] if compound_values else 0
        final_simple = simple_values[-1] if simple_values else 0
        compound_benefit = final_compound - final_simple
        
        return {
            'compound_benefit': compound_benefit,
            'simple_vs_compound': {
                'simple': final_simple,
                'compound': final_compound
            },
            'monthly_compound_rates': monthly_rates,
            'compound_progression': compound_values,
            'simple_progression': simple_values
        }
    
    def generate_future_scenarios(self, months_ahead: int = 12, scenarios: List[float] = None) -> Dict[str, List[float]]:
        """
        将来シナリオを生成
        
        Args:
            months_ahead (int): 予測期間（月数）
            scenarios (List[float]): 年率リターンシナリオ（%）
            
        Returns:
            Dict[str, List[float]]: シナリオ別予測結果
        """
        if scenarios is None:
            scenarios = [-10, -5, 0, 3, 5, 7, 10, 15]  # 年率リターン（%）
        
        if self.df.empty:
            current_value = 0
            avg_monthly_investment = 30000  # デフォルト値
        else:
            latest = self.monthly_data.iloc[-1]
            current_value = latest['累計評価額']
            active_investments = self.monthly_data[self.monthly_data['投資額'] > 0]['投資額']
            avg_monthly_investment = active_investments.mean() if len(active_investments) > 0 else 30000
        
        scenario_results = {}
        
        for annual_return in scenarios:
            monthly_return = annual_return / 100 / 12
            future_values = []
            
            value = current_value
            for month in range(months_ahead):
                # 既存資産の成長
                value = value * (1 + monthly_return)
                # 新規投資
                value += avg_monthly_investment
                future_values.append(value)
            
            scenario_results[f'{annual_return}%'] = future_values
        
        return scenario_results
    
    def analyze_investment_timing(self) -> Dict[str, any]:
        """
        投資タイミングの分析
        
        Returns:
            Dict[str, any]: タイミング分析結果
        """
        if len(self.monthly_data) < 3:
            return {
                'best_months': [],
                'worst_months': [],
                'timing_score': 0.0,
                'consistency_score': 0.0
            }
        
        # 月次パフォーマンス
        monthly_performance = []
        for i, row in self.monthly_data.iterrows():
            if row['投資額'] > 0:
                monthly_return = row['月次リターン率']
                monthly_performance.append({
                    'year': row['年'],
                    'month': row['月'],
                    'return': monthly_return,
                    'investment': row['投資額']
                })
        
        if not monthly_performance:
            return {
                'best_months': [],
                'worst_months': [],
                'timing_score': 0.0,
                'consistency_score': 0.0
            }
        
        # パフォーマンスでソート
        sorted_performance = sorted(monthly_performance, key=lambda x: x['return'], reverse=True)
        
        # ベスト・ワースト月
        best_months = sorted_performance[:3]
        worst_months = sorted_performance[-3:]
        
        # タイミングスコア（高リターン時の投資額加重平均）
        total_weighted_return = sum(p['return'] * p['investment'] for p in monthly_performance)
        total_investment = sum(p['investment'] for p in monthly_performance)
        timing_score = total_weighted_return / total_investment if total_investment > 0 else 0
        
        # 一貫性スコア（投資額の変動係数の逆数）
        investments = [p['investment'] for p in monthly_performance]
        if len(investments) > 1:
            cv = np.std(investments) / np.mean(investments)  # 変動係数
            consistency_score = 1 / (1 + cv)  # 0-1のスコア
        else:
            consistency_score = 1.0
        
        return {
            'best_months': best_months,
            'worst_months': worst_months,
            'timing_score': timing_score,
            'consistency_score': consistency_score
        }