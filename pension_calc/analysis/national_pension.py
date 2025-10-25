"""
国民年金分析モジュール

国民年金の詳細分析と最適化を行う
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from pension_calc.core.pension_utils import (
    DEFAULT_NATIONAL_PENSION_HISTORY,
    generate_national_pension_projection
)

class NationalPensionAnalyzer:
    """国民年金分析クラス"""
    
    def __init__(self):
        """初期化"""
        self.history = DEFAULT_NATIONAL_PENSION_HISTORY
    
    def calculate_lifetime_value(
        self, 
        start_age: int = 20, 
        retirement_age: int = 65,
        life_expectancy: int = 85
    ) -> Dict:
        """
        国民年金の生涯価値を計算
        
        Args:
            start_age: 加入開始年齢
            retirement_age: 受給開始年齢
            life_expectancy: 平均寿命
            
        Returns:
            生涯価値分析結果
        """
        # 加入期間（月数）
        contribution_months = (retirement_age - start_age) * 12
        
        # 受給期間（月数）
        receiving_months = (life_expectancy - retirement_age) * 12
        
        # 満額基礎年金（令和5年度）
        full_basic_pension_annual = 780900
        full_basic_pension_monthly = full_basic_pension_annual / 12
        
        # 加入月数に応じた受給額計算
        max_contribution_months = 40 * 12  # 40年 = 480ヶ月
        actual_contribution_months = min(contribution_months, max_contribution_months)
        
        monthly_pension = full_basic_pension_monthly * (actual_contribution_months / max_contribution_months)
        annual_pension = monthly_pension * 12
        
        # 平均保険料（簡易計算）
        average_monthly_fee = np.mean([h["月額保険料"] for h in self.history])
        
        # 総納付額
        total_contribution = average_monthly_fee * actual_contribution_months
        
        # 総受給額
        total_benefit = monthly_pension * receiving_months
        
        # 損益
        net_benefit = total_benefit - total_contribution
        roi = (net_benefit / total_contribution * 100) if total_contribution > 0 else 0
        
        return {
            "加入月数": actual_contribution_months,
            "受給月数": receiving_months,
            "月額受給額": monthly_pension,
            "年額受給額": annual_pension,
            "総納付額": total_contribution,
            "総受給額": total_benefit,
            "純利益": net_benefit,
            "投資利回り相当": roi,
            "損益分岐年数": (total_contribution / annual_pension) if annual_pension > 0 else float('inf')
        }
    
    def optimize_receiving_age(
        self, 
        start_age: int = 20,
        life_expectancy: int = 85
    ) -> Dict:
        """
        最適な受給開始年齢を分析
        
        Args:
            start_age: 加入開始年齢
            life_expectancy: 平均寿命
            
        Returns:
            最適化分析結果
        """
        results = {}
        
        # 60歳〜75歳の範囲で分析
        for receiving_age in range(60, 76):
            result = self.calculate_lifetime_value(start_age, receiving_age, life_expectancy)
            results[receiving_age] = result
        
        # 最適年齢を特定（純利益最大）
        best_age = max(results.keys(), key=lambda age: results[age]["純利益"])
        
        return {
            "最適受給開始年齢": best_age,
            "最大純利益": results[best_age]["純利益"],
            "全年齢結果": results
        }
    
    def analyze_fee_impact(self) -> Dict:
        """
        保険料変動の影響を分析
        
        Returns:
            保険料影響分析結果
        """
        years = [h["年度"] for h in self.history]
        fees = [h["月額保険料"] for h in self.history]
        
        # 成長率計算
        growth_rates = []
        for i in range(1, len(fees)):
            growth_rate = (fees[i] - fees[i-1]) / fees[i-1] * 100
            growth_rates.append(growth_rate)
        
        avg_growth_rate = np.mean(growth_rates) if growth_rates else 0
        
        # 将来予測
        years_actual, _, future_years, future_fees = generate_national_pension_projection(avg_growth_rate/100)
        
        return {
            "実績保険料": dict(zip(years, fees)),
            "年間成長率": growth_rates,
            "平均成長率": avg_growth_rate,
            "将来予測": dict(zip(future_years, future_fees)),
            "最新保険料": fees[-1],
            "予測最高保険料": max(future_fees) if future_fees else fees[-1]
        }

def analyze_contribution_strategies() -> Dict:
    """
    納付戦略を分析
    
    Returns:
        戦略分析結果
    """
    analyzer = NationalPensionAnalyzer()
    
    strategies = {
        "標準戦略": analyzer.calculate_lifetime_value(20, 65, 85),
        "早期受給": analyzer.calculate_lifetime_value(20, 60, 85),
        "晩期受給": analyzer.calculate_lifetime_value(20, 70, 85),
        "短期加入": analyzer.calculate_lifetime_value(30, 65, 85),
        "長寿対応": analyzer.calculate_lifetime_value(20, 65, 95)
    }
    
    # 最良戦略を特定
    best_strategy = max(strategies.keys(), key=lambda s: strategies[s]["純利益"])
    
    return {
        "戦略比較": strategies,
        "推奨戦略": best_strategy,
        "推奨理由": f"純利益が最大（{strategies[best_strategy]['純利益']:,.0f}円）"
    }

if __name__ == "__main__":
    # 分析実行例
    analyzer = NationalPensionAnalyzer()
    
    print("=== 国民年金分析 ===")
    
    # 基本分析
    basic_result = analyzer.calculate_lifetime_value()
    print(f"基本ケース純利益: {basic_result['純利益']:,.0f}円")
    print(f"損益分岐年数: {basic_result['損益分岐年数']:.1f}年")
    
    # 最適受給年齢
    optimization_result = analyzer.optimize_receiving_age()
    print(f"最適受給開始年齢: {optimization_result['最適受給開始年齢']}歳")
    print(f"最大純利益: {optimization_result['最大純利益']:,.0f}円")
    
    # 戦略比較
    strategy_result = analyze_contribution_strategies()
    print(f"推奨戦略: {strategy_result['推奨戦略']}")
    print(f"推奨理由: {strategy_result['推奨理由']}")