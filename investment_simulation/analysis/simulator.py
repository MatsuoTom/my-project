"""
投資シミュレーションモジュール

将来予測、目標達成シミュレーション、最適化提案
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import plotly.graph_objects as go


class InvestmentSimulator:
    """
    投資シミュレーションを実行するクラス
    """
    
    def __init__(self, parsed_data: pd.DataFrame):
        """
        Args:
            parsed_data: パース済みデータ
        """
        self.data = parsed_data.copy()
        self.data = self.data.sort_values('発生日').reset_index(drop=True)
    
    def simulate_future_value(
        self,
        years: int = 5,
        monthly_investment: float = None,
        scenarios: List[float] = [0.03, 0.05, 0.07, 0.10]
    ) -> Dict:
        """
        将来価値をシミュレーション（複数シナリオ）
        
        Args:
            years: 予測年数
            monthly_investment: 月次投資額（Noneの場合は過去の平均を使用）
            scenarios: 年率リターンシナリオのリスト
            
        Returns:
            Dict: シミュレーション結果
        """
        # 現在の保有状況
        current_value = self.data['評価金額'].iloc[-1]
        current_quantity = self.data['保有数量'].iloc[-1]
        
        # 月次投資額の推定
        if monthly_investment is None:
            buy_df = self.data[self.data['取引区分'] == '買付']
            if len(buy_df) > 0:
                total_months = (buy_df['発生日'].max() - buy_df['発生日'].min()).days / 30
                if total_months > 0:
                    monthly_investment = buy_df['金額(円)'].sum() / total_months
                else:
                    monthly_investment = buy_df['金額(円)'].mean()
            else:
                monthly_investment = 0
        
        results = {}
        months = years * 12
        
        for annual_return in scenarios:
            monthly_return = (1 + annual_return) ** (1/12) - 1
            
            # 月次シミュレーション
            values = [current_value]
            investments = [0]
            
            for month in range(1, months + 1):
                # 前月の評価額に月次リターンを適用
                prev_value = values[-1]
                new_value = prev_value * (1 + monthly_return)
                
                # 新規投資を追加
                new_value += monthly_investment
                
                values.append(new_value)
                investments.append(monthly_investment)
            
            total_investment = sum(investments)
            final_value = values[-1]
            total_return = final_value - current_value - total_investment
            return_rate = (total_return / (current_value + total_investment)) * 100 if (current_value + total_investment) > 0 else 0
            
            results[f'シナリオ_{int(annual_return*100)}%'] = {
                '年率リターン': annual_return * 100,
                '最終評価額': final_value,
                '追加投資額': total_investment,
                '総投資額': current_value + total_investment,
                '総利益': total_return,
                'リターン率': return_rate,
                '月次評価額': values
            }
        
        return {
            '現在評価額': current_value,
            '月次投資額': monthly_investment,
            'シミュレーション期間': years,
            'シナリオ結果': results
        }
    
    def calculate_goal_achievement(
        self,
        target_amount: float,
        monthly_investment: float = None,
        expected_return: float = 0.05
    ) -> Dict:
        """
        目標金額到達シミュレーション
        
        Args:
            target_amount: 目標金額
            monthly_investment: 月次投資額（Noneの場合は過去平均）
            expected_return: 期待年率リターン
            
        Returns:
            Dict: 達成予測結果
        """
        current_value = self.data['評価金額'].iloc[-1]
        
        # 既に目標達成している場合
        if current_value >= target_amount:
            return {
                '目標金額': target_amount,
                '現在評価額': current_value,
                'ステータス': '達成済み',
                '超過額': current_value - target_amount
            }
        
        # 月次投資額の推定
        if monthly_investment is None:
            buy_df = self.data[self.data['取引区分'] == '買付']
            if len(buy_df) > 0:
                total_months = (buy_df['発生日'].max() - buy_df['発生日'].min()).days / 30
                if total_months > 0:
                    monthly_investment = buy_df['金額(円)'].sum() / total_months
                else:
                    monthly_investment = buy_df['金額(円)'].mean()
            else:
                monthly_investment = 0
        
        # 月次リターン
        monthly_return = (1 + expected_return) ** (1/12) - 1
        
        # 月次シミュレーション
        value = current_value
        month = 0
        max_months = 600  # 最大50年
        
        while value < target_amount and month < max_months:
            value = value * (1 + monthly_return) + monthly_investment
            month += 1
        
        years = month / 12
        total_investment = monthly_investment * month
        
        # 必要月額の計算（逆算）
        required_monthly = self._calculate_required_monthly_investment(
            current_value, target_amount, expected_return, years
        )
        
        return {
            '目標金額': target_amount,
            '現在評価額': current_value,
            '不足額': target_amount - current_value,
            '月次投資額': monthly_investment,
            '期待年率リターン': expected_return * 100,
            '到達予想期間_月': month,
            '到達予想期間_年': years,
            '追加投資総額': total_investment,
            '最終評価額': value,
            '必要月額_最小': required_monthly
        }
    
    def _calculate_required_monthly_investment(
        self,
        current_value: float,
        target_value: float,
        annual_return: float,
        years: float
    ) -> float:
        """
        目標達成に必要な月次投資額を計算
        
        Args:
            current_value: 現在評価額
            target_value: 目標金額
            annual_return: 年率リターン
            years: 期間（年）
            
        Returns:
            float: 必要月次投資額
        """
        if years <= 0:
            return 0
        
        monthly_return = (1 + annual_return) ** (1/12) - 1
        months = int(years * 12)
        
        # 現在の評価額が目標期間でどれだけ成長するか
        future_current_value = current_value * ((1 + monthly_return) ** months)
        
        # 不足分
        shortage = target_value - future_current_value
        
        if shortage <= 0:
            return 0
        
        # 複利年金の現在価値公式の逆算
        if monthly_return == 0:
            return shortage / months
        
        # FV = PMT * [((1 + r)^n - 1) / r]
        # PMT = FV / [((1 + r)^n - 1) / r]
        fv_factor = (((1 + monthly_return) ** months) - 1) / monthly_return
        required_monthly = shortage / fv_factor
        
        return max(0, required_monthly)
    
    def compare_investment_strategies(
        self,
        strategies: Dict[str, Dict],
        years: int = 10
    ) -> Dict:
        """
        複数の投資戦略を比較
        
        Args:
            strategies: 戦略辞書 {'戦略名': {'monthly': 月額, 'return': リターン}}
            years: シミュレーション期間
            
        Returns:
            Dict: 比較結果
        """
        current_value = self.data['評価金額'].iloc[-1]
        results = {}
        
        for strategy_name, params in strategies.items():
            monthly = params.get('monthly', 0)
            annual_return = params.get('return', 0.05)
            monthly_return = (1 + annual_return) ** (1/12) - 1
            
            value = current_value
            total_investment = 0
            
            for month in range(years * 12):
                value = value * (1 + monthly_return) + monthly
                total_investment += monthly
            
            profit = value - current_value - total_investment
            return_rate = (profit / (current_value + total_investment)) * 100 if (current_value + total_investment) > 0 else 0
            
            results[strategy_name] = {
                '最終評価額': value,
                '追加投資額': total_investment,
                '利益': profit,
                'リターン率': return_rate
            }
        
        return results
    
    def plot_future_scenarios(self, simulation_result: Dict) -> go.Figure:
        """
        将来シナリオをプロット
        
        Args:
            simulation_result: simulate_future_value()の結果
            
        Returns:
            go.Figure: グラフオブジェクト
        """
        fig = go.Figure()
        
        years = simulation_result['シミュレーション期間']
        months = list(range(years * 12 + 1))
        
        for scenario_name, data in simulation_result['シナリオ結果'].items():
            fig.add_trace(go.Scatter(
                x=months,
                y=data['月次評価額'],
                mode='lines',
                name=scenario_name,
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title=f'{years}年後の評価額予測（複数シナリオ）',
            xaxis_title='経過月数',
            yaxis_title='評価額（円）',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def optimize_monthly_investment(
        self,
        target_amount: float,
        deadline_years: int,
        expected_return: float = 0.05,
        max_monthly: float = None
    ) -> Dict:
        """
        目標達成のための最適月次投資額を計算
        
        Args:
            target_amount: 目標金額
            deadline_years: 期限（年）
            expected_return: 期待年率リターン
            max_monthly: 最大月額（制約）
            
        Returns:
            Dict: 最適化結果
        """
        current_value = self.data['評価金額'].iloc[-1]
        
        required_monthly = self._calculate_required_monthly_investment(
            current_value, target_amount, expected_return, deadline_years
        )
        
        # 制約チェック
        is_feasible = True
        if max_monthly is not None and required_monthly > max_monthly:
            is_feasible = False
            # 最大月額での到達可能額を計算
            monthly_return = (1 + expected_return) ** (1/12) - 1
            months = int(deadline_years * 12)
            
            future_current = current_value * ((1 + monthly_return) ** months)
            fv_factor = (((1 + monthly_return) ** months) - 1) / monthly_return
            max_achievable = future_current + (max_monthly * fv_factor)
            
            shortage = target_amount - max_achievable
        else:
            max_achievable = target_amount
            shortage = 0
        
        return {
            '目標金額': target_amount,
            '現在評価額': current_value,
            '期限': deadline_years,
            '期待リターン': expected_return * 100,
            '必要月額': required_monthly,
            '最大月額制約': max_monthly,
            '実行可能': is_feasible,
            '最大到達可能額': max_achievable,
            '不足額': shortage if not is_feasible else 0,
            '追加必要期間_年': (shortage / (max_monthly * 12)) if (not is_feasible and max_monthly and max_monthly > 0) else 0
        }
