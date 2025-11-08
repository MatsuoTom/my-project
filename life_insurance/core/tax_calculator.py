"""
税額計算モジュール

所得税・住民税の計算と節税効果を算出します。
"""

from typing import Dict, List, Tuple
import pandas as pd
from datetime import datetime


class TaxCalculator:
    """税額計算クラス"""

    # 2025年現在の所得税率表（復興特別所得税含む）
    INCOME_TAX_BRACKETS = [
        (1950000, 0.0515),  # 195万円以下: 5% + 復興税0.315%
        (3300000, 0.1021),  # 195万円超～330万円以下: 10% + 復興税0.21%
        (6950000, 0.2042),  # 330万円超～695万円以下: 20% + 復興税0.42%
        (9000000, 0.2353),  # 695万円超～900万円以下: 23% + 復興税0.483%
        (18000000, 0.3372),  # 900万円超～1800万円以下: 33% + 復興税0.693%
        (40000000, 0.4084),  # 1800万円超～4000万円以下: 40% + 復興税0.84%
        (float("inf"), 0.4599),  # 4000万円超: 45% + 復興税0.945%
    ]

    # 住民税率（全国一律）
    RESIDENCE_TAX_RATE = 0.10  # 10%

    def __init__(self):
        """コンストラクタ"""
        self.current_year = datetime.now().year

    def get_income_tax_rate(self, taxable_income: float) -> float:
        """
        課税所得に基づく所得税率を取得（復興特別所得税含む）

        Args:
            taxable_income: 課税所得

        Returns:
            所得税率（復興特別所得税含む）
        """
        for threshold, rate in self.INCOME_TAX_BRACKETS:
            if taxable_income <= threshold:
                return rate

        return self.INCOME_TAX_BRACKETS[-1][1]  # 最高税率

    def calculate_income_tax(self, taxable_income: float) -> Dict[str, float]:
        """
        所得税を計算（復興特別所得税含む）

        Args:
            taxable_income: 課税所得

        Returns:
            所得税計算の詳細
        """
        if taxable_income <= 0:
            return {"課税所得": 0, "適用税率": 0, "所得税": 0, "復興特別所得税": 0, "合計所得税": 0}

        # 累進課税の計算
        remaining_income = taxable_income
        total_tax = 0
        applied_rate = 0

        # 控除額テーブル（速算用）
        deduction_table = [
            (1950000, 0, 0.0515),
            (3300000, 97500, 0.1021),
            (6950000, 427500, 0.2042),
            (9000000, 636000, 0.2353),
            (18000000, 1536000, 0.3372),
            (40000000, 2796000, 0.4084),
            (float("inf"), 4796000, 0.4599),
        ]

        for threshold, deduction, rate in deduction_table:
            if taxable_income <= threshold:
                total_tax = taxable_income * rate - deduction
                applied_rate = rate
                break

        # 基本所得税と復興特別所得税を分離
        base_income_tax = total_tax / (1 + 0.021)  # 復興税率2.1%を除く
        reconstruction_tax = total_tax - base_income_tax

        return {
            "課税所得": taxable_income,
            "適用税率": applied_rate,
            "所得税": base_income_tax,
            "復興特別所得税": reconstruction_tax,
            "合計所得税": total_tax,
        }

    def calculate_tax_savings(
        self, deduction_amount: float, taxable_income: float
    ) -> Dict[str, float]:
        """
        控除による節税効果を計算

        Args:
            deduction_amount: 控除額
            taxable_income: 控除前の課税所得

        Returns:
            節税効果の詳細
        """
        # 控除前の税額
        before_tax = self.calculate_income_tax(taxable_income)
        before_residence_tax = taxable_income * self.RESIDENCE_TAX_RATE

        # 控除後の税額
        after_income = max(0, taxable_income - deduction_amount)
        after_tax = self.calculate_income_tax(after_income)
        after_residence_tax = after_income * self.RESIDENCE_TAX_RATE

        # 節税効果計算
        income_tax_savings = before_tax["合計所得税"] - after_tax["合計所得税"]
        residence_tax_savings = before_residence_tax - after_residence_tax
        total_savings = income_tax_savings + residence_tax_savings

        return {
            "控除額": deduction_amount,
            "控除前課税所得": taxable_income,
            "控除後課税所得": after_income,
            "控除前所得税": before_tax["合計所得税"],
            "控除後所得税": after_tax["合計所得税"],
            "所得税節税額": income_tax_savings,
            "控除前住民税": before_residence_tax,
            "控除後住民税": after_residence_tax,
            "住民税節税額": residence_tax_savings,
            "合計節税額": total_savings,
            "実効節税率": total_savings / deduction_amount if deduction_amount > 0 else 0,
        }

    def get_tax_bracket_info(self, taxable_income: float) -> Dict[str, any]:
        """
        現在の税額区分情報を取得

        Args:
            taxable_income: 課税所得

        Returns:
            税額区分の詳細情報
        """
        current_rate = self.get_income_tax_rate(taxable_income)

        # 次の税額区分を探す
        next_bracket = None
        for threshold, rate in self.INCOME_TAX_BRACKETS:
            if taxable_income < threshold:
                next_bracket = {"閾値": threshold, "税率": rate, "差額": threshold - taxable_income}
                break

        # 前の税額区分を探す
        prev_bracket = None
        for i, (threshold, rate) in enumerate(self.INCOME_TAX_BRACKETS):
            if taxable_income <= threshold:
                if i > 0:
                    prev_threshold, prev_rate = self.INCOME_TAX_BRACKETS[i - 1]
                    prev_bracket = {
                        "閾値": prev_threshold,
                        "税率": prev_rate,
                        "差額": taxable_income - prev_threshold,
                    }
                break

        return {
            "現在の課税所得": taxable_income,
            "現在の税率": current_rate,
            "前の区分": prev_bracket,
            "次の区分": next_bracket,
        }

    def simulate_income_changes(
        self, base_income: float, income_changes: List[float], deduction_amount: float = 0
    ) -> pd.DataFrame:
        """
        所得変動による税額・節税効果の変化をシミュレーション

        Args:
            base_income: 基準所得
            income_changes: 所得変動額のリスト
            deduction_amount: 控除額

        Returns:
            シミュレーション結果のDataFrame
        """
        results = []

        for change in income_changes:
            new_income = base_income + change

            if new_income < 0:
                continue

            savings = self.calculate_tax_savings(deduction_amount, new_income)

            results.append(
                {
                    "所得変動": change,
                    "課税所得": new_income,
                    "所得税率": f"{self.get_income_tax_rate(new_income):.2%}",
                    "控除額": deduction_amount,
                    "所得税節税額": savings["所得税節税額"],
                    "住民税節税額": savings["住民税節税額"],
                    "合計節税額": savings["合計節税額"],
                    "実効節税率": f"{savings['実効節税率']:.2%}",
                }
            )

        return pd.DataFrame(results)


def main():
    """デモンストレーション用のメイン関数"""
    calculator = TaxCalculator()

    print("=== 税額計算デモ ===")

    # 基本的な税額計算
    test_incomes = [3000000, 5000000, 7000000, 10000000]

    print("\n1. 所得別税額計算:")
    for income in test_incomes:
        tax_info = calculator.calculate_income_tax(income)
        print(
            f"課税所得: {income:,}円 → 所得税: {tax_info['合計所得税']:,.0f}円 "
            f"(税率: {tax_info['適用税率']:.2%})"
        )

    # 節税効果計算
    print("\n2. 控除による節税効果:")
    deduction = 50000  # 最大控除額
    for income in test_incomes:
        savings = calculator.calculate_tax_savings(deduction, income)
        print(
            f"課税所得: {income:,}円 → 節税額: {savings['合計節税額']:,.0f}円 "
            f"(実効節税率: {savings['実効節税率']:.2%})"
        )

    # 所得変動シミュレーション
    print("\n3. 所得変動による節税効果の変化:")
    base_income = 5000000
    income_changes = [-1000000, -500000, 0, 500000, 1000000]
    simulation = calculator.simulate_income_changes(base_income, income_changes, deduction)

    print(f"基準所得: {base_income:,}円, 控除額: {deduction:,}円")
    print(
        simulation[["所得変動", "課税所得", "所得税率", "合計節税額", "実効節税率"]].to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
