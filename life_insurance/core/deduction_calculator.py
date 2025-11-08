"""
旧生命保険料控除の節税効果計算モジュール

旧生命保険料控除制度（平成23年12月31日以前の契約）の
控除額計算と節税効果を算出します。
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime


class LifeInsuranceDeductionCalculator:
    """旧生命保険料控除の計算クラス"""

    # 旧生命保険料控除の控除額テーブル
    OLD_DEDUCTION_TABLE = [
        (25000, 0.5, 0),  # 25,000円以下: 支払保険料×1/2
        (50000, 0.25, 12500),  # 25,001円～50,000円: 支払保険料×1/4+12,500円
        (100000, 0.2, 15000),  # 50,001円～100,000円: 支払保険料×1/5+15,000円
        (float("inf"), 0, 50000),  # 100,001円以上: 50,000円（上限）
    ]

    def __init__(self):
        """コンストラクタ"""
        self.current_year = datetime.now().year

    def calculate_old_deduction(self, annual_premium: float) -> float:
        """
        旧生命保険料控除額を計算

        Args:
            annual_premium: 年間支払保険料

        Returns:
            控除額
        """
        if annual_premium <= 0:
            return 0

        for threshold, rate, base_amount in self.OLD_DEDUCTION_TABLE:
            if annual_premium <= threshold:
                return min(annual_premium * rate + base_amount, 50000)

        return 50000  # 最大控除額

    def get_deduction_breakdown(self, annual_premium: float) -> Dict[str, float]:
        """
        控除額の詳細内訳を取得

        Args:
            annual_premium: 年間支払保険料

        Returns:
            控除計算の詳細情報
        """
        deduction = self.calculate_old_deduction(annual_premium)

        # どの段階の控除率が適用されたかを判定
        applied_bracket = None
        for i, (threshold, rate, base_amount) in enumerate(self.OLD_DEDUCTION_TABLE):
            if annual_premium <= threshold:
                applied_bracket = i
                break

        bracket_names = [
            "第1段階（25,000円以下）",
            "第2段階（25,001円～50,000円）",
            "第3段階（50,001円～100,000円）",
            "第4段階（100,001円以上）",
        ]

        return {
            "年間支払保険料": annual_premium,
            "控除額": deduction,
            "適用段階": bracket_names[applied_bracket] if applied_bracket is not None else "不明",
            "控除率": deduction / annual_premium if annual_premium > 0 else 0,
            "上限到達": deduction >= 50000,
        }

    def calculate_multiple_contracts(self, contracts: List[float]) -> Dict[str, float]:
        """
        複数の保険契約がある場合の合計控除額を計算

        Args:
            contracts: 各契約の年間支払保険料のリスト

        Returns:
            合計控除額の詳細
        """
        total_premium = sum(contracts)
        individual_deductions = [self.calculate_old_deduction(premium) for premium in contracts]
        total_individual = sum(individual_deductions)
        combined_deduction = self.calculate_old_deduction(total_premium)

        return {
            "契約数": len(contracts),
            "合計支払保険料": total_premium,
            "個別計算時の控除額合計": total_individual,
            "合算計算時の控除額": combined_deduction,
            "最適な控除額": max(total_individual, combined_deduction),
            "個別計算が有利": total_individual > combined_deduction,
            "節約効果": abs(total_individual - combined_deduction),
        }

    def optimize_premium_distribution(
        self, total_budget: float, num_contracts: int = 2
    ) -> Dict[str, any]:
        """
        控除額を最大化する保険料配分を計算

        Args:
            total_budget: 総予算
            num_contracts: 契約数

        Returns:
            最適配分の詳細
        """
        if num_contracts <= 1:
            return {
                "最適配分": [total_budget],
                "合計控除額": self.calculate_old_deduction(total_budget),
                "総予算": total_budget,
            }

        best_deduction = 0
        best_distribution = []

        # 各契約の保険料を1000円刻みで最適化
        step = 1000
        max_per_contract = min(100000, total_budget)  # 上限額での計算効率化

        def generate_distributions(remaining_budget, remaining_contracts, current_dist):
            nonlocal best_deduction, best_distribution

            if remaining_contracts == 1:
                # 最後の契約に残り予算を全て割り当て
                final_dist = current_dist + [remaining_budget]
                total_deduction = sum(
                    self.calculate_old_deduction(premium) for premium in final_dist
                )

                if total_deduction > best_deduction:
                    best_deduction = total_deduction
                    best_distribution = final_dist.copy()
                return

            # 現在の契約への割り当てを試行
            max_allocation = min(max_per_contract, remaining_budget)
            for allocation in range(0, int(max_allocation) + 1, step):
                if remaining_budget - allocation >= 0:
                    generate_distributions(
                        remaining_budget - allocation,
                        remaining_contracts - 1,
                        current_dist + [allocation],
                    )

        generate_distributions(total_budget, num_contracts, [])

        return {
            "最適配分": best_distribution,
            "合計控除額": best_deduction,
            "総予算": total_budget,
            "契約数": num_contracts,
            "平均控除率": best_deduction / total_budget if total_budget > 0 else 0,
        }


def main():
    """デモンストレーション用のメイン関数"""
    calculator = LifeInsuranceDeductionCalculator()

    print("=== 旧生命保険料控除計算デモ ===")

    # 基本計算例
    test_premiums = [30000, 60000, 80000, 120000]

    print("\n1. 基本的な控除額計算:")
    for premium in test_premiums:
        breakdown = calculator.get_deduction_breakdown(premium)
        print(
            f"保険料: {premium:,}円 → 控除額: {breakdown['控除額']:,}円 "
            f"({breakdown['適用段階']}, 控除率: {breakdown['控除率']:.1%})"
        )

    # 複数契約の比較
    print("\n2. 複数契約の最適化:")
    contracts = [40000, 60000]
    result = calculator.calculate_multiple_contracts(contracts)
    print(f"契約1: {contracts[0]:,}円, 契約2: {contracts[1]:,}円")
    print(f"個別計算: {result['個別計算時の控除額合計']:,}円")
    print(f"合算計算: {result['合算計算時の控除額']:,}円")
    print(
        f"最適: {result['最適な控除額']:,}円 ({'個別' if result['個別計算が有利'] else '合算'}計算)"
    )

    # 最適配分計算
    print("\n3. 最適な保険料配分:")
    total_budget = 150000
    optimization = calculator.optimize_premium_distribution(total_budget, 3)
    print(f"総予算: {total_budget:,}円")
    print(f"最適配分: {[f'{p:,}円' for p in optimization['最適配分']]}")
    print(f"合計控除額: {optimization['合計控除額']:,}円")
    print(f"平均控除率: {optimization['平均控除率']:.1%}")


if __name__ == "__main__":
    main()
